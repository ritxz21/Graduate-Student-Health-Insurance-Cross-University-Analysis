"""
config.py — Central configuration for the grad insurance project.

Contains:
  - UNIVERSITIES: full list of 50 target schools with IDs, metadata, and known URLs
  - FIELD_NAMES: ordered list matching the tracking sheet columns
  - COST_FIELD_NAMES / COVERAGE_FIELD_NAMES / etc.: grouped subsets for convenience
  - DATA_DIR / OUTPUTS_DIR: path helpers (relative to project root)
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR      = PROJECT_ROOT / "data"
RAW_PDF_DIR   = DATA_DIR / "raw"
OUTPUTS_DIR   = PROJECT_ROOT / "outputs"
TRACKING_XLSX = DATA_DIR / "tracking_sheet.xlsx"

RAW_PDF_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# University registry
# Each entry is a dict with keys matching the tracking sheet identifier fields.
# source_url_secondary is a semicolon-separated string (may be empty).
# ---------------------------------------------------------------------------
UNIVERSITIES = [
    # ── Ivy League (target: 8, all northeast, all private) ──────────────────
    {
        "university_id":   "harvard",
        "university_name": "Harvard University",
        "university_type": "ivy_league",
        "control":         "private",
        "region":          "northeast",
        "state":           "MA",
        "source_url_primary":   "https://hushp.harvard.edu/",
        "source_url_secondary": "",
    },
    {
        "university_id":   "yale",
        "university_name": "Yale University",
        "university_type": "ivy_league",
        "control":         "private",
        "region":          "northeast",
        "state":           "CT",
        "source_url_primary":   "https://yalehealth.yale.edu/insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "princeton",
        "university_name": "Princeton University",
        "university_type": "ivy_league",
        "control":         "private",
        "region":          "northeast",
        "state":           "NJ",
        "source_url_primary":   "https://uhs.princeton.edu/health-insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "columbia",
        "university_name": "Columbia University",
        "university_type": "ivy_league",
        "control":         "private",
        "region":          "northeast",
        "state":           "NY",
        "source_url_primary":   "https://health.columbia.edu/content/student-insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "upenn",
        "university_name": "University of Pennsylvania",
        "university_type": "ivy_league",
        "control":         "private",
        "region":          "northeast",
        "state":           "PA",
        "source_url_primary":   "https://srfs.upenn.edu/student-insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "cornell",
        "university_name": "Cornell University",
        "university_type": "ivy_league",
        "control":         "private",
        "region":          "northeast",
        "state":           "NY",
        "source_url_primary":   "https://studenthealthbenefits.cornell.edu/",
        "source_url_secondary": "",
    },
    {
        "university_id":   "brown",
        "university_name": "Brown University",
        "university_type": "ivy_league",
        "control":         "private",
        "region":          "northeast",
        "state":           "RI",
        "source_url_primary":   "https://www.brown.edu/campus-life/health/services/insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "dartmouth",
        "university_name": "Dartmouth College",
        "university_type": "ivy_league",
        "control":         "private",
        "region":          "northeast",
        "state":           "NH",
        "source_url_primary":   "https://students.dartmouth.edu/health-service/insurance/overview",
        "source_url_secondary": "",
    },
    # ── Large public R1s (target: 17, all public) ───────────────────────────
    # Northeast (3)
    {
        "university_id":   "rutgers_nb",
        "university_name": "Rutgers University–New Brunswick",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "northeast",
        "state":           "NJ",
        "source_url_primary":   "https://finance.rutgers.edu/student-abc/insurance-students/student-health-insurance-plan-ship",
        "source_url_secondary": "https://www.universityhealthplans.com/letters/letter.cgi?group_id=269",
    },
    {
        "university_id":   "suny_buffalo",
        "university_name": "University at Buffalo (SUNY)",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "northeast",
        "state":           "NY",
        "source_url_primary":   "https://www.buffalo.edu/studentaccounts/ship.html",
        "source_url_secondary": "",
    },
    {
        "university_id":   "penn_state",
        "university_name": "Penn State University",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "northeast",
        "state":           "PA",
        "source_url_primary":   "https://studentaffairs.psu.edu/health/insurance",
        "source_url_secondary": "",
    },
    # Midwest (6)
    {
        "university_id":   "umich_ann_arbor",
        "university_name": "University of Michigan–Ann Arbor",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "midwest",
        "state":           "MI",
        "source_url_primary":   "https://hr.umich.edu/benefits-wellness/health-well-being/health-plans/gradcare",
        "source_url_secondary": "",
    },
    {
        "university_id":   "uw_madison",
        "university_name": "University of Wisconsin-Madison",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "midwest",
        "state":           "WI",
        "source_url_primary":   "https://www.uhs.wisc.edu/patient-services/insurance/",
        "source_url_secondary": "",
    },
    {
        "university_id":   "umn_twin_cities",
        "university_name": "University of Minnesota-Twin Cities",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "midwest",
        "state":           "MN",
        "source_url_primary":   "https://boynton.umn.edu/insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "ohio_state",
        "university_name": "Ohio State University",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "midwest",
        "state":           "OH",
        "source_url_primary":   "https://shs.osu.edu/health-insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "uiuc",
        "university_name": "University of Illinois Urbana-Champaign",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "midwest",
        "state":           "IL",
        "source_url_primary":   "https://humanresources.illinois.edu/cms/One.aspx?portalId=4292&pageId=5570",
        "source_url_secondary": "",
    },
    {
        "university_id":   "indiana_bloomington",
        "university_name": "Indiana University Bloomington",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "midwest",
        "state":           "IN",
        "source_url_primary":   "https://studentaffairs.indiana.edu/student-health/insurance/index.html",
        "source_url_secondary": "",
    },
    # South (5)
    {
        "university_id":   "ut_austin",
        "university_name": "University of Texas at Austin",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "south",
        "state":           "TX",
        "source_url_primary":   "https://gradschool.utexas.edu/grad-life/health-wellness/insurance",
        "source_url_secondary": "https://hr.utexas.edu/student/student-employee-insurance-benefits/academic-graduate-student-employee-insurance-options",
    },
    {
        "university_id":   "unc_chapel_hill",
        "university_name": "University of North Carolina at Chapel Hill",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "south",
        "state":           "NC",
        "source_url_primary":   "https://studentaffairs.unc.edu/student-wellness/student-insurance/",
        "source_url_secondary": "",
    },
    {
        "university_id":   "u_florida",
        "university_name": "University of Florida",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "south",
        "state":           "FL",
        "source_url_primary":   "https://shcc.ufl.edu/insurance/",
        "source_url_secondary": "",
    },
    {
        "university_id":   "u_virginia",
        "university_name": "University of Virginia",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "south",
        "state":           "VA",
        "source_url_primary":   "https://www.studenthealth.virginia.edu/insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "georgia_tech",
        "university_name": "Georgia Institute of Technology",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "south",
        "state":           "GA",
        "source_url_primary":   "https://health.gatech.edu/insurance",
        "source_url_secondary": "",
    },
    # West (5)
    {
        "university_id":   "uc_berkeley",
        "university_name": "University of California, Berkeley",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "west",
        "state":           "CA",
        "source_url_primary":   "https://uhs.berkeley.edu/ship",
        "source_url_secondary": "",
    },
    {
        "university_id":   "ucla",
        "university_name": "University of California, Los Angeles",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "west",
        "state":           "CA",
        "source_url_primary":   "https://www.studenthealth.ucla.edu/insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "u_washington",
        "university_name": "University of Washington",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "west",
        "state":           "WA",
        "source_url_primary":   "https://wellbeing.uw.edu/unit/ship/",
        "source_url_secondary": "",
    },
    {
        "university_id":   "u_arizona",
        "university_name": "University of Arizona",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "west",
        "state":           "AZ",
        "source_url_primary":   "https://health.arizona.edu/student-insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "u_colorado_boulder",
        "university_name": "University of Colorado Boulder",
        "university_type": "r1_public",
        "control":         "public",
        "region":          "west",
        "state":           "CO",
        "source_url_primary":   "https://www.colorado.edu/health/student-health-insurance-plan",
        "source_url_secondary": "",
    },
    # ── Mid-size privates (target: 10, all private) ──────────────────────────
    {
        "university_id":   "northwestern",
        "university_name": "Northwestern University",
        "university_type": "mid_size_private",
        "control":         "private",
        "region":          "midwest",
        "state":           "IL",
        "source_url_primary":   "https://www.northwestern.edu/student-insurance/",
        "source_url_secondary": "",
    },
    {
        "university_id":   "u_chicago",
        "university_name": "University of Chicago",
        "university_type": "mid_size_private",
        "control":         "private",
        "region":          "midwest",
        "state":           "IL",
        "source_url_primary":   "https://wellness.uchicago.edu/medical/student-insurance-program/",
        "source_url_secondary": "",
    },
    {
        "university_id":   "wustl",
        "university_name": "Washington University in St. Louis",
        "university_type": "mid_size_private",
        "control":         "private",
        "region":          "midwest",
        "state":           "MO",
        "source_url_primary":   "https://students.wustl.edu/student-health-insurance/",
        "source_url_secondary": "",
    },
    {
        "university_id":   "duke",
        "university_name": "Duke University",
        "university_type": "mid_size_private",
        "control":         "private",
        "region":          "south",
        "state":           "NC",
        "source_url_primary":   "https://students.duke.edu/wellness/studenthealth/insurance/",
        "source_url_secondary": "https://gradschool.duke.edu/financial-support/medical-and-dental-insurance/",
    },
    {
        "university_id":   "vanderbilt",
        "university_name": "Vanderbilt University",
        "university_type": "mid_size_private",
        "control":         "private",
        "region":          "south",
        "state":           "TN",
        "source_url_primary":   "https://www.vanderbilt.edu/student-health/studentinsurance.php",
        "source_url_secondary": "",
    },
    {
        "university_id":   "emory",
        "university_name": "Emory University",
        "university_type": "mid_size_private",
        "control":         "private",
        "region":          "south",
        "state":           "GA",
        "source_url_primary":   "https://studenthealth.emory.edu/sh/insurance/index.html",
        "source_url_secondary": "",
    },
    {
        "university_id":   "rice",
        "university_name": "Rice University",
        "university_type": "mid_size_private",
        "control":         "private",
        "region":          "south",
        "state":           "TX",
        "source_url_primary":   "https://wellness.rice.edu/student-health-insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "stanford",
        "university_name": "Stanford University",
        "university_type": "mid_size_private",
        "control":         "private",
        "region":          "west",
        "state":           "CA",
        "source_url_primary":   "https://studentinsurance.stanford.edu/",
        "source_url_secondary": "https://vaden.stanford.edu/insurance-referral-office",
    },
    {
        "university_id":   "usc",
        "university_name": "University of Southern California",
        "university_type": "mid_size_private",
        "control":         "private",
        "region":          "west",
        "state":           "CA",
        "source_url_primary":   "https://enroll.myschi.com/usc",
        "source_url_secondary": "",
    },
    {
        "university_id":   "carnegie_mellon",
        "university_name": "Carnegie Mellon University",
        "university_type": "mid_size_private",
        "control":         "private",
        "region":          "northeast",
        "state":           "PA",
        "source_url_primary":   "https://www.cmu.edu/health-services/student-insurance/index.html",
        "source_url_secondary": "",
    },
    # ── Regional publics (target: 8, non-flagship public) ───────────────────
    {
        "university_id":   "sdsu",
        "university_name": "San Diego State University",
        "university_type": "regional_public",
        "control":         "public",
        "region":          "west",
        "state":           "CA",
        "source_url_primary":   "https://sdsu.studenthealthinsurance.net/",
        "source_url_secondary": "",
    },
    {
        "university_id":   "csulb",
        "university_name": "California State University, Long Beach",
        "university_type": "regional_public",
        "control":         "public",
        "region":          "west",
        "state":           "CA",
        "source_url_primary":   "https://www.csulb.edu/student-health-services/student-health-insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "portland_state",
        "university_name": "Portland State University",
        "university_type": "regional_public",
        "control":         "public",
        "region":          "west",
        "state":           "OR",
        "source_url_primary":   "https://www.pdx.edu/student-health/insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "u_north_texas",
        "university_name": "University of North Texas",
        "university_type": "regional_public",
        "control":         "public",
        "region":          "south",
        "state":           "TX",
        "source_url_primary":   "https://studentaffairs.unt.edu/student-health/student-health-insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "georgia_state",
        "university_name": "Georgia State University",
        "university_type": "regional_public",
        "control":         "public",
        "region":          "south",
        "state":           "GA",
        "source_url_primary":   "https://sfs.gsu.edu/resources/student-health-insurance/insurance-plans/",
        "source_url_secondary": "",
    },
    {
        "university_id":   "northern_illinois",
        "university_name": "Northern Illinois University",
        "university_type": "regional_public",
        "control":         "public",
        "region":          "midwest",
        "state":           "IL",
        "source_url_primary":   "https://www.niu.edu/student_insurance/",
        "source_url_secondary": "",
    },
    {
        "university_id":   "wichita_state",
        "university_name": "Wichita State University",
        "university_type": "regional_public",
        "control":         "public",
        "region":          "midwest",
        "state":           "KS",
        "source_url_primary":   "https://www.wichita.edu/student_life/shs/insurance.php",
        "source_url_secondary": "",
    },
    {
        "university_id":   "umas_boston",
        "university_name": "University of Massachusetts Boston",
        "university_type": "regional_public",
        "control":         "public",
        "region":          "northeast",
        "state":           "MA",
        "source_url_primary":   "https://www.umb.edu/registrar/student_services/student_health_insurance",
        "source_url_secondary": "",
    },
    # ── Liberal arts colleges with graduate programs (target: 4) ─────────────
    {
        "university_id":   "williams",
        "university_name": "Williams College",
        "university_type": "liberal_arts",
        "control":         "private",
        "region":          "northeast",
        "state":           "MA",
        "source_url_primary":   "https://studentfinancialservices.williams.edu/student-health-insurance/",
        "source_url_secondary": "",
    },
    {
        "university_id":   "amherst",
        "university_name": "Amherst College",
        "university_type": "liberal_arts",
        "control":         "private",
        "region":          "northeast",
        "state":           "MA",
        "source_url_primary":   "https://www.amherst.edu/campuslife/health-safety-wellness/health/insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "middlebury",
        "university_name": "Middlebury College",
        "university_type": "liberal_arts",
        "control":         "private",
        "region":          "northeast",
        "state":           "VT",
        "source_url_primary":   "https://www.middlebury.edu/student-financial-services/financial-tools-and-resources/student-health-insurance",
        "source_url_secondary": "https://go.gallagherstudent.com/Universities/Middlebury%20College/Home",
    },
    {
        "university_id":   "wesleyan",
        "university_name": "Wesleyan University",
        "university_type": "liberal_arts",
        "control":         "private",
        "region":          "northeast",
        "state":           "CT",
        "source_url_primary":   "https://www.wesleyan.edu/studentaffairs/studentwellness/insurance.html",
        "source_url_secondary": "",
    },
    # ── Professional-degree-heavy (target: 3) ───────────────────────────────
    {
        "university_id":   "thomas_jefferson",
        "university_name": "Thomas Jefferson University",
        "university_type": "professional_heavy",
        "control":         "private",
        "region":          "northeast",
        "state":           "PA",
        "source_url_primary":   "https://www.jefferson.edu/life-at-jefferson/health-wellness/student-health-insurance-plan.html",
        "source_url_secondary": "https://www.universityhealthplans.com/Jefferson",
    },
    {
        "university_id":   "yeshiva",
        "university_name": "Yeshiva University",
        "university_type": "professional_heavy",
        "control":         "private",
        "region":          "northeast",
        "state":           "NY",
        "source_url_primary":   "https://www.yu.edu/student-life/student-health-services/insurance",
        "source_url_secondary": "",
    },
    {
        "university_id":   "babson",
        "university_name": "Babson College",
        "university_type": "professional_heavy",
        "control":         "private",
        "region":          "northeast",
        "state":           "MA",
        "source_url_primary":   "https://www.babson.edu/student-experience/health-wellness/health-services/",
        "source_url_secondary": "",
    },
]

# Quick lookup by university_id
UNIVERSITY_BY_ID = {u["university_id"]: u for u in UNIVERSITIES}

# ---------------------------------------------------------------------------
# Tracking sheet field order (must match the Tracking sheet column headers)
# ---------------------------------------------------------------------------
TRACKING_FIELDS = [
    "university_id", "plan_variant", "university_name", "data_collection_date",
    "plan_year", "source_url_primary", "source_url_secondary", "source_type",
    "university_type", "control", "region", "state", "grad_enrollment_approx",
    "grad_union_present", "grad_union_strength", "grad_union_name",
    "carrier", "administrator", "network_type", "system_plan_id",
    "premium_annual_usd", "premium_period_source", "premium_subsidy_type",
    "premium_subsidy_eligibility",
    "deductible_in_network_usd", "deductible_out_of_network_usd",
    "oop_max_in_network_usd", "oop_max_out_of_network_usd",
    "primary_care_copay_usd", "primary_care_coinsurance_pct",
    "mental_health_covered", "mental_health_copay_usd", "mental_health_session_limit",
    "prescription_drug_covered", "preventive_care_covered_100pct",
    "maternity_covered", "dental_included_in_medical", "vision_included_in_medical",
    "dependent_coverage_available", "dependent_premium_annual_usd_spouse",
    "dependent_premium_annual_usd_child", "dependent_subsidy_available",
    "enrollment_auto", "waiver_available", "waiver_deadline_strict",
    "international_students_required",
    "degree_type_differentiation", "master_plan_same_as_phd",
    "phd_plan_same_as_professional",
    "collection_status", "extraction_method", "manual_override_fields",
    "data_quality_flag", "notes",
]

# ---------------------------------------------------------------------------
# Known system plans — used to auto-populate system_plan_id
# ---------------------------------------------------------------------------
SYSTEM_PLAN_MAP = {
    "uc_berkeley": "uc_ship",
    "ucla":        "uc_ship",
    "georgia_state":   "usg_ship",
    "suny_buffalo":    "suny_ship",
}

# ---------------------------------------------------------------------------
# Known union information (as of data collection start, April 2025)
# Sources: CGEU member list, UAW Academic Workers, school HR pages
# ---------------------------------------------------------------------------
KNOWN_UNIONS = {
    "harvard":          {"grad_union_present": 1, "grad_union_strength": "contract",    "grad_union_name": "HGSU-UAW Local 5118"},
    "umich_ann_arbor":  {"grad_union_present": 1, "grad_union_strength": "contract",    "grad_union_name": "GEO (AFT Local 3550)"},
    "uc_berkeley":      {"grad_union_present": 1, "grad_union_strength": "contract",    "grad_union_name": "UAW Local 4811"},
    "ucla":             {"grad_union_present": 1, "grad_union_strength": "contract",    "grad_union_name": "UAW Local 4811"},
    "u_washington":     {"grad_union_present": 1, "grad_union_strength": "contract",    "grad_union_name": "UAW Local 4121"},
    "rutgers_nb":       {"grad_union_present": 1, "grad_union_strength": "contract",    "grad_union_name": "Rutgers AAUP-AFT"},
    "uw_madison":       {"grad_union_present": 1, "grad_union_strength": "contract",    "grad_union_name": "TAA (AFT Local 3220)"},
    "uiuc":             {"grad_union_present": 1, "grad_union_strength": "contract",    "grad_union_name": "GEO Local 6300"},
    "u_florida":        {"grad_union_present": 1, "grad_union_strength": "contract",    "grad_union_name": "UFF-Graduate Assistants United"},
    "columbia":         {"grad_union_present": 1, "grad_union_strength": "contract",    "grad_union_name": "SWC-UAW Local 2110"},
    "yale":             {"grad_union_present": 1, "grad_union_strength": "contract",    "grad_union_name": "GESO/UNITE HERE Local 33"},
    "u_chicago":        {"grad_union_present": 1, "grad_union_strength": "contract",    "grad_union_name": "Graduate Students United (UE)"},
    "northwestern":     {"grad_union_present": 1, "grad_union_strength": "recognized",  "grad_union_name": "NUGW-UE"},
    "cornell":          {"grad_union_present": 1, "grad_union_strength": "contract",    "grad_union_name": "CGSU-AFT"},
    "ut_austin":        {"grad_union_present": 0, "grad_union_strength": "none",        "grad_union_name": ""},
    "duke":             {"grad_union_present": 0, "grad_union_strength": "none",        "grad_union_name": ""},
    "stanford":         {"grad_union_present": 0, "grad_union_strength": "none",        "grad_union_name": ""},
    "georgia_state":    {"grad_union_present": 0, "grad_union_strength": "none",        "grad_union_name": ""},
    "thomas_jefferson": {"grad_union_present": 0, "grad_union_strength": "none",        "grad_union_name": ""},
    "middlebury":       {"grad_union_present": 0, "grad_union_strength": "none",        "grad_union_name": ""},
}

# ---------------------------------------------------------------------------
# HTTP request headers — polite browser-like headers to avoid 403s
# ---------------------------------------------------------------------------
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# How long to wait between requests (seconds) to be a polite scraper
REQUEST_DELAY_SECONDS = 2.0

# Timeout for HTTP requests
REQUEST_TIMEOUT_SECONDS = 20
