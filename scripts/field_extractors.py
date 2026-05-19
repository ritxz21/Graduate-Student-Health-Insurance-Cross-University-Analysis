"""
field_extractors.py - Rule-based extraction of every field in the data dictionary.

Missing-value conventions:
  - Numeric fields not found  -> None
  - String fields not found   -> ""
  - Binary fields with no signal -> 0 (conservative)

Public API:
  extract_all_fields(text, uni_id="") -> dict
"""

from __future__ import annotations
import re
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _s(pattern, text, flags=re.IGNORECASE):
    return re.search(pattern, text, flags)

def _dollar(raw):
    raw = raw.replace("$", "").replace(",", "").strip()
    try:
        v = float(raw)
        return int(v) if v == int(v) else round(v, 2)
    except ValueError:
        return None

def _pct(raw):
    raw = raw.replace("%", "").strip()
    try:
        v = float(raw)
        return int(v) if v == int(v) else round(v, 1)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Cost fields
# ---------------------------------------------------------------------------

_PREMIUM_KW = (
    r"(?:annual\s+)?premium|plan\s+(?:cost|rate|fee)|"
    r"(?:student\s+)?(?:health\s+)?insurance\s+(?:cost|rate|fee|premium)|"
    r"(?:ship\s+rate|enrollment\s+fee)"
)

def extract_premium(text):
    patterns = [
        (r"\$([\d,]+(?:\.\d{1,2})?)\s*/?\s*(?:per\s+)?(?:academic\s+)?year", "annual"),
        (r"\$([\d,]+(?:\.\d{1,2})?)\s+(?:per\s+)?(?:academic\s+)?year", "annual"),
        (r"\$([\d,]+(?:\.\d{1,2})?)\s+annually", "annual"),
        (r"\$([\d,]+(?:\.\d{1,2})?)\s+per\s+semester", "semester"),
        (r"\$([\d,]+(?:\.\d{1,2})?)\s+per\s+month", "monthly"),
        (r"\$([\d,]+(?:\.\d{1,2})?)\s+monthly", "monthly"),
    ]
    mult = {"annual": 1, "semester": 2, "quarterly": 4, "monthly": 12}
    for pat, period in patterns:
        m = _s(pat, text)
        if m:
            v = _dollar(m.group(1))
            if v:
                return v * mult.get(period, 1), period
    # fallback: look near keyword
    m = _s(_PREMIUM_KW, text)
    if m:
        snippet = text[max(0, m.start()-150): min(len(text), m.end()+150)]
        amounts = re.findall(r"\$[\d,]+(?:\.\d{1,2})?", snippet, re.IGNORECASE)
        if amounts:
            v = _dollar(amounts[0])
            if v:
                return v, "annual"
    return None, ""


def extract_deductible(text):
    in_net = None
    out_net = None
    for pat in [
        r"deductible[^$\n]{0,60}in[- ]network[^$\n]{0,60}\$([\d,]+)",
        r"in[- ]network[^$\n]{0,60}deductible[^$\n]{0,60}\$([\d,]+)",
        r"(?:individual\s+)?deductible[^$\n]{0,60}\$([\d,]+)",
        r"\$([\d,]+)[^$\n]{0,60}deductible",
    ]:
        m = _s(pat, text)
        if m:
            in_net = _dollar(m.group(1))
            break
    if _s(r"no\s+deductible|\$0\s+deductible|zero\s+deductible", text):
        in_net = 0
    for pat in [
        r"out[- ]of[- ]network[^$\n]{0,60}deductible[^$\n]{0,60}\$([\d,]+)",
        r"deductible[^$\n]{0,60}out[- ]of[- ]network[^$\n]{0,60}\$([\d,]+)",
    ]:
        m = _s(pat, text)
        if m:
            out_net = _dollar(m.group(1))
            break
    return in_net, out_net


def extract_oop_max(text):
    in_net = None
    out_net = None
    kw = r"out[- ]of[- ]pocket\s+(?:maximum|max|limit|stop[- ]loss)"
    for pat in [
        rf"{kw}[^$\n]{{0,80}}in[- ]network[^$\n]{{0,60}}\$([\d,]+)",
        rf"in[- ]network[^$\n]{{0,60}}{kw}[^$\n]{{0,60}}\$([\d,]+)",
        rf"{kw}[^$\n]{{0,60}}\$([\d,]+)",
        rf"\$([\d,]+)[^$\n]{{0,60}}{kw}",
    ]:
        m = _s(pat, text)
        if m:
            in_net = _dollar(m.group(1))
            break
    for pat in [
        rf"out[- ]of[- ]network[^$\n]{{0,80}}{kw}[^$\n]{{0,60}}\$([\d,]+)",
        rf"{kw}[^$\n]{{0,80}}out[- ]of[- ]network[^$\n]{{0,60}}\$([\d,]+)",
    ]:
        m = _s(pat, text)
        if m:
            out_net = _dollar(m.group(1))
            break
    return in_net, out_net


def extract_primary_care_cost(text):
    copay = None
    coins = None
    for pat in [
        r"primary\s+care[^$\n]{0,60}copay[^$\n]{0,30}\$([\d]+)",
        r"office\s+visit[^$\n]{0,60}copay[^$\n]{0,30}\$([\d]+)",
        r"\$([\d]+)\s+copay[^$\n]{0,60}(?:primary|office\s+visit)",
        r"copay[^$\n]{0,60}\$([\d]+)",
    ]:
        m = _s(pat, text)
        if m:
            copay = _dollar(m.group(1))
            break
    if copay is None:
        for pat in [
            r"primary\s+care[^%\n]{0,60}([\d]+)\s*%",
            r"office\s+visit[^%\n]{0,60}([\d]+)\s*%\s+coinsurance",
        ]:
            m = _s(pat, text)
            if m:
                coins = _pct(m.group(1))
                break
    return copay, coins


# ---------------------------------------------------------------------------
# Coverage features
# ---------------------------------------------------------------------------

_MH_KW = ["mental health", "behavioral health", "psychiatric", "psychological",
           "counseling", "therapy", "psychotherapy", "mental wellness"]

def extract_mental_health_covered(text):
    lower = text.lower()
    for pat in [r"mental\s+health.{0,60}not\s+covered",
                r"mental\s+health.{0,60}exclud",
                r"no\s+mental\s+health\s+(?:coverage|benefit)"]:
        if _s(pat, lower):
            return "0_not_covered"
    if not any(kw in lower for kw in _MH_KW):
        return "2_standard"
    enhanced = ["enhanced", "no session limit", "unlimited sessions",
                "zero copay", r"\$0 copay", "no cost sharing"]
    if any(_s(sig, lower) for sig in enhanced):
        return "3_enhanced"
    limited = ["session limit", "session cap", r"\d+\s+visit", r"\d+\s+session",
               "not covered", "excluded", "exclusion"]
    if any(_s(sig, lower) for sig in limited):
        return "1_limited"
    return "2_standard"


def extract_mental_health_copay(text):
    for pat in [
        r"(?:mental|behavioral)\s+health[^$\n]{0,80}\$([\d]+)\s+copay",
        r"(?:mental|behavioral)\s+health[^$\n]{0,80}copay[^$\n]{0,30}\$([\d]+)",
        r"(?:outpatient\s+)?(?:mental|behavioral|psychiatric)[^$\n]{0,60}\$([\d]+)",
    ]:
        m = _s(pat, text)
        if m:
            return _dollar(m.group(1))
    return None


def extract_mental_health_session_limit(text):
    for pat in [
        r"(\d+)\s+(?:outpatient\s+)?(?:mental\s+health|behavioral\s+health)\s+(?:visits?|sessions?)",
        r"(?:mental|behavioral)\s+health.{0,60}(\d+)\s+(?:visits?|sessions?)\s+(?:per\s+year|annually)",
        r"(?:limit|cap|maximum)\s+of\s+(\d+)\s+(?:visits?|sessions?)[^.]{0,60}(?:mental|behavioral)",
    ]:
        m = _s(pat, text)
        if m:
            v = int(m.group(1))
            if 1 <= v <= 365:
                return v
    return None


def _bin(text, pos, neg=None):
    lower = text.lower()
    neg = neg or []
    if any(kw in lower for kw in neg):
        return 0
    return 1 if any(kw in lower for kw in pos) else 0


def extract_prescription_covered(text):
    return _bin(text, ["prescription", "rx", "pharmacy", "drug coverage"],
                ["prescription not covered"])

def extract_preventive_100pct(text):
    return _bin(text, ["preventive care", "preventive services", "100%", "no cost", "aca"])

def extract_maternity(text):
    return _bin(text, ["maternity", "obstetric", "prenatal", "pregnancy", "childbirth"],
                ["maternity not covered"])

def extract_dental_bundled(text):
    lower = text.lower()
    if re.search(r"dental.{0,60}(?:included|covered|bundled)", lower):
        return 1
    if re.search(r"(?:medical\s+and\s+dental|health\s+and\s+dental)\s+insurance", lower):
        return 1
    return 0

def extract_vision_bundled(text):
    return 1 if re.search(r"vision.{0,60}(?:included|covered|bundled)", text, re.I) else 0


# ---------------------------------------------------------------------------
# Dependents
# ---------------------------------------------------------------------------

def extract_dependent_coverage(text):
    return _bin(text, ["dependent", "spouse", "domestic partner", "child", "family coverage"])

def extract_dependent_premium_spouse(text):
    for pat in [r"spouse[^$\n]{0,60}\$([\d,]+)",
                r"domestic\s+partner[^$\n]{0,60}\$([\d,]+)",
                r"\$([\d,]+)[^$\n]{0,60}(?:spouse|domestic\s+partner)"]:
        m = _s(pat, text)
        if m:
            return _dollar(m.group(1))
    return None

def extract_dependent_premium_child(text):
    for pat in [r"child(?:ren)?[^$\n]{0,60}\$([\d,]+)",
                r"\$([\d,]+)[^$\n]{0,60}child(?:ren)?"]:
        m = _s(pat, text)
        if m:
            return _dollar(m.group(1))
    return None

def extract_dependent_subsidy(text):
    lower = text.lower()
    for sig in ["dependent subsidy", "dependent insurance fund",
                "university pays dependent", "employer contribution"]:
        if sig in lower:
            return 1
    if re.search(r"university.{0,60}contribution.{0,60}dependent", lower):
        return 1
    return 0


# ---------------------------------------------------------------------------
# Waiver / enrollment
# ---------------------------------------------------------------------------

def extract_enrollment_auto(text):
    sigs = ["automatically enrolled", "auto-enrolled", "auto enrolled",
            "charged unless waived", "billed unless you opt out", "waive the plan"]
    return 1 if any(s in text.lower() for s in sigs) else 0

def extract_waiver_available(text):
    return _bin(text, ["waiver", "waive", "opt out", "opt-out"])

def extract_waiver_deadline_strict(text):
    lower = text.lower()
    return 1 if any(s in lower for s in ["no refund", "non-refundable",
                                          "missed deadline", "retroactive"]) else 0

def extract_international_required(text):
    lower = text.lower()
    sigs = [r"f-1", r"j-1", r"f/j", r"international student.{0,40}required",
            r"visa.{0,40}required"]
    return 1 if any(re.search(s, lower) for s in sigs) else 0


# ---------------------------------------------------------------------------
# Network type
# ---------------------------------------------------------------------------

def extract_network_type(text):
    for pat, val in [
        (r"\bppo\b", "ppo"), (r"\bhmo\b", "hmo"),
        (r"\bepo\b", "epo"), (r"\bpos\b", "pos"),
        (r"tiered\s+network|tier\s+1|tier\s+2", "tiered"),
    ]:
        if _s(pat, text):
            return val
    return "unknown"


# ---------------------------------------------------------------------------
# Carrier / administrator
# ---------------------------------------------------------------------------

_CARRIERS = [
    (r"blue\s+cross\s+blue\s+shield\s+of\s+(?:massachusetts|mass\.?)", "Blue Cross Blue Shield of Massachusetts"),
    (r"\bbcbs[- ]?ma\b", "Blue Cross Blue Shield of Massachusetts"),
    (r"blue\s+cross\s+blue\s+shield", "Blue Cross Blue Shield"),
    (r"\bbcbs\b", "Blue Cross Blue Shield"),
    (r"blue\s+care\s+network", "Blue Care Network (BCN)"),
    (r"unitedhealthcare|\buhc\b", "UnitedHealthcare"),
    (r"\baetna\b", "Aetna"),
    (r"\bcigna\b", "Cigna"),
    (r"\bwellfleet\b", "Wellfleet"),
    (r"\banthem\b", "Anthem"),
    (r"\bhumana\b", "Humana"),
    (r"\bkaiser\b", "Kaiser Permanente"),
]

_ADMINS = [
    (r"gallagher\s+student", "Gallagher Student Health"),
    (r"academic\s+health\s+plans?|\bahp\b", "Academic Health Plans (AHP)"),
    (r"university\s+health\s+plans?", "University Health Plans"),
    (r"\buhcsr\b", "UHCSR"),
    (r"\bwellfleet\b", "Wellfleet"),
]

def extract_carrier(text):
    for pat, name in _CARRIERS:
        if _s(pat, text):
            return name
    return "unknown"

def extract_administrator(text):
    for pat, name in _ADMINS:
        if _s(pat, text):
            return name
    return ""


# ---------------------------------------------------------------------------
# Degree-type differentiation
# ---------------------------------------------------------------------------

# Separate plans by degree type (master's vs PhD vs professional)
_DEG_SIGNALS = [
    r"master.{0,30}(?:student|plan|program).{0,60}(?:phd|doctoral)",
    r"phd.{0,60}master.{0,60}(?:different|separate|distinct)\s+plan",
    r"separate\s+(?:plan|coverage|option).{0,60}(?:master|phd|doctoral|professional)",
    r"professional\s+degree.{0,60}(?:different|separate)\s+plan",
]

# Separate plans by employment status — use explicit, specific phrases only
_EMP_SIGNALS = [
    r"teaching\s+assistants?\s+(?:are\s+)?(?:eligible|covered|enrolled|receive).{0,60}(?:plan|coverage)",
    r"research\s+assistants?\s+(?:are\s+)?(?:eligible|covered|enrolled|receive).{0,60}(?:plan|coverage)",
    r"graduate\s+(?:employees?|assistants?|instructors?)\s+(?:are\s+)?eligible.{0,60}(?:plan|coverage)",
    r"\b(?:gsi|gssa|gsra|gra|gta)\b\s+(?:plan|coverage|eligible|benefit)",
    r"benefit[- ]eligible\s+graduate\s+(?:student|employee)",
    r"employment\s+status\s+determines\s+(?:coverage|plan|eligibility)",
    r"two[- ]plan\s+structure|dual[- ]plan\s+structure",
    r"gradcare.{0,40}(?:dship|ship)|dship.{0,40}gradcare",
]

# Same plan, different who-pays
_SUBSIDY_SIGNALS = [
    r"(?:phd|doctoral)\s+(?:student|candidate).{0,60}premium.{0,60}(?:paid|covered|waived|university)",
    r"university.{0,60}(?:pays|covers|waives).{0,60}premium.{0,60}(?:phd|doctoral)",
    r"master.{0,20}student.{0,60}(?:pay|responsible).{0,60}premium",
    r"funding\s+status\s+determines.{0,60}(?:cost|premium|coverage)",
]

def extract_degree_type_differentiation(text):
    lower = text.lower()
    for pat in _DEG_SIGNALS:
        if _s(pat, lower):
            return "separate_by_degree"
    for pat in _EMP_SIGNALS:
        if _s(pat, lower):
            return "separate_by_employment"
    for pat in _SUBSIDY_SIGNALS:
        if _s(pat, lower):
            return "subsidy_differs_only"
    has_degree = bool(_s(r"\b(?:master|phd|doctoral|professional\s+degree)\b", lower))
    has_plan = bool(_s(r"\b(?:plan|coverage|premium|option)\b", lower))
    if has_degree and has_plan:
        return "unclear"
    return "uniform"

def extract_master_same_as_phd(text, deg_diff):
    if deg_diff in ("separate_by_degree", "separate_by_employment"):
        return 0
    if deg_diff in ("subsidy_differs_only", "uniform"):
        return 1
    return None


# ---------------------------------------------------------------------------
# Union info
# ---------------------------------------------------------------------------

def extract_union_info(text, uni_id=""):
    try:
        from config import KNOWN_UNIONS
        if uni_id in KNOWN_UNIONS:
            return KNOWN_UNIONS[uni_id]
    except ImportError:
        pass

    lower = text.lower()
    union_kw = ["graduate employee union", "graduate student union",
                "collective bargaining", "labor agreement", "bargaining unit",
                "uaw local", "aft local", "seiu", "ue local", "aaup",
                "gso", "geu", "geo ", "cgsu"]
    if not any(kw in lower for kw in union_kw):
        return {"grad_union_present": 0, "grad_union_strength": "none", "grad_union_name": ""}

    nm = re.search(
        r"(?:uaw|aft|seiu|ue|aaup)[- ]?(?:local\s+)?[\d]+|"
        r"graduate\s+(?:employee|student|workers?)\s+(?:union|organization|association)",
        text, re.IGNORECASE)
    name = nm.group(0).strip() if nm else ""
    strength = "contract" if re.search(
        r"collective\s+bargaining\s+agreement|labor\s+agreement", lower) else "recognized"
    return {"grad_union_present": 1, "grad_union_strength": strength, "grad_union_name": name}


# ---------------------------------------------------------------------------
# Plan year
# ---------------------------------------------------------------------------

def extract_plan_year(text):
    for pat in [r"20\d{2}[--]\s*20\d{2}",
                r"academic\s+year\s+20\d{2}[--]20\d{2}",
                r"(?:plan|policy)\s+year\s+20\d{2}[--]20\d{2}"]:
        m = _s(pat, text)
        if m:
            raw = re.sub(r"[-–]\s*", "-", m.group(0))
            yr = re.search(r"20\d{2}-20\d{2}", raw)
            if yr:
                return yr.group(0)
    return ""


# ---------------------------------------------------------------------------
# Master extractor
# ---------------------------------------------------------------------------

def extract_all_fields(text, uni_id=""):
    """Run all extractors and return a dict of field_name -> value."""
    premium, pperiod = extract_premium(text)
    ded_in, ded_out  = extract_deductible(text)
    oop_in, oop_out  = extract_oop_max(text)
    copay, coins     = extract_primary_care_cost(text)
    mh               = extract_mental_health_covered(text)
    mh_copay         = extract_mental_health_copay(text)
    mh_sess          = extract_mental_health_session_limit(text)
    deg_diff         = extract_degree_type_differentiation(text)
    union            = extract_union_info(text, uni_id)

    result = {
        "plan_year":                        extract_plan_year(text),
        "carrier":                          extract_carrier(text),
        "administrator":                    extract_administrator(text),
        "network_type":                     extract_network_type(text),
        "premium_annual_usd":               premium,
        "premium_period_source":            pperiod,
        "deductible_in_network_usd":        ded_in,
        "deductible_out_of_network_usd":    ded_out,
        "oop_max_in_network_usd":           oop_in,
        "oop_max_out_of_network_usd":       oop_out,
        "primary_care_copay_usd":           copay,
        "primary_care_coinsurance_pct":     coins,
        "mental_health_covered":            mh,
        "mental_health_copay_usd":          mh_copay,
        "mental_health_session_limit":      mh_sess,
        "prescription_drug_covered":        extract_prescription_covered(text),
        "preventive_care_covered_100pct":   extract_preventive_100pct(text),
        "maternity_covered":                extract_maternity(text),
        "dental_included_in_medical":       extract_dental_bundled(text),
        "vision_included_in_medical":       extract_vision_bundled(text),
        "dependent_coverage_available":         extract_dependent_coverage(text),
        "dependent_premium_annual_usd_spouse":  extract_dependent_premium_spouse(text),
        "dependent_premium_annual_usd_child":   extract_dependent_premium_child(text),
        "dependent_subsidy_available":          extract_dependent_subsidy(text),
        "enrollment_auto":                  extract_enrollment_auto(text),
        "waiver_available":                 extract_waiver_available(text),
        "waiver_deadline_strict":           extract_waiver_deadline_strict(text),
        "international_students_required":  extract_international_required(text),
        "degree_type_differentiation":      deg_diff,
        "master_plan_same_as_phd":          extract_master_same_as_phd(text, deg_diff),
        "phd_plan_same_as_professional":    None,
    }
    result.update(union)
    return result
