"""
AI Course Finder – v10 (tightened)

- No Safer / Realistic / Reach scoring.
- Recommendations strictly adhere to Tab 1 preferences:
  - Degree levels
  - Interest areas
  - Max tuition (if specified)
  - Location preference (in-state only when chosen)
- Interest areas offered in the form (v10):
  Engineering, Computer Science, Business, Healthcare, Arts
"""

import json
import os
from typing import Any, Dict, List, Optional

from flask import Flask, render_template, request, session

# ---------------------------------------------------------------------------
# Basic config
# ---------------------------------------------------------------------------

APP_NAME = "AI Course Finder"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "programs_v7.json")

SECRET_KEY_ENV = "COURSE_FINDER_V10_SECRET_KEY"

app = Flask(
    __name__,
    template_folder=BASE_DIR,
    static_folder=BASE_DIR,
    static_url_path="",
)
app.secret_key = os.environ.get(SECRET_KEY_ENV, "dev-course-finder-v10-change-me")

# Cache for loaded programs
_program_cache: Optional[List[Dict[str, Any]]] = None

# Domain options
US_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]

# Match dataset degree_level values directly
DEGREE_OPTIONS = ["Certificate", "Associate", "Bachelor's"]

# v10 interest options shown in the form (simplified)
INTEREST_OPTIONS = [
    "Engineering",
    "Computer Science",
    "Business",
    "Healthcare",
    "Arts",
]

# Weights for ranking (fit score)
INTEREST_WEIGHT = 70.0
DEGREE_WEIGHT = 20.0
LOCATION_WEIGHT = 10.0


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_programs() -> List[Dict[str, Any]]:
    """
    Load demo programs from programs_v7.json.
    Normalizes some fields for safe downstream use.
    """
    global _program_cache
    if _program_cache is not None:
        return _program_cache

    programs: List[Dict[str, Any]] = []

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except FileNotFoundError:
        print(f"[WARN] Data file not found: {DATA_PATH}")
        _program_cache = []
        return _program_cache
    except json.JSONDecodeError:
        print(f"[WARN] Could not decode JSON from: {DATA_PATH}")
        _program_cache = []
        return _program_cache

    if not isinstance(raw, list):
        raw = []

    for item in raw:
        if not isinstance(item, dict):
            continue

        p = dict(item)

        # Normalize tuition
        tuition = p.get("annual_tuition")
        try:
            p["annual_tuition"] = float(tuition) if tuition not in (None, "") else None
        except (TypeError, ValueError):
            p["annual_tuition"] = None

        # Normalize list-like fields
        for key in ("interest_areas", "delivery_modes"):
            value = p.get(key) or []
            if isinstance(value, list):
                p[key] = value
            elif isinstance(value, str):
                p[key] = [v.strip() for v in value.split(",") if v.strip()]
            else:
                p[key] = []

        programs.append(p)

    _program_cache = programs
    return _program_cache


# ---------------------------------------------------------------------------
# Scoring helpers (no safety buckets in v10)
# ---------------------------------------------------------------------------

def _selectivity_target_gpa(selectivity_band: Optional[str]) -> float:
    """
    Map selectivity band to an approximate target GPA.
    Used only for descriptive academic explanations, not for buckets.
    """
    band = (selectivity_band or "").lower()
    if band == "highly_selective":
        return 3.7
    if band == "selective":
        return 3.3
    if band == "moderate":
        return 2.8
    # "open" / broad access or unknown
    return 2.3


def _build_interests_reason(
    pref_interests: "set[str]",
    program_interests: "set[str]",
) -> str:
    overlap = pref_interests & program_interests
    if overlap:
        return "Matches your interest areas: " + ", ".join(sorted(overlap)) + "."
    if not pref_interests:
        return "Offers a broad curriculum suitable for exploring different interests."
    return "Offers related fields where you may discover new interests."


def _build_academic_reason(
    gpa: float,
    selectivity_band: Optional[str],
) -> str:
    """
    Provide a descriptive academic fit explanation, without safety/target/reach buckets.
    """
    if gpa <= 0 or not selectivity_band:
        return (
            "Academic context is based on general patterns; your GPA or the school's "
            "selectivity band is not fully specified."
        )

    target_gpa = _selectivity_target_gpa(selectivity_band)
    delta = gpa - target_gpa

    if delta >= 0.3:
        return (
            "Your GPA is somewhat above the typical range for this school, which suggests "
            "a comfortable academic match."
        )
    if delta >= -0.2:
        return (
            "Your GPA is roughly in line with the typical range for this school, which "
            "suggests a reasonable academic match."
        )
    return (
        "This school is more academically competitive than your current GPA range. "
        "It may be more challenging, but could still be worth considering."
    )


def _build_practical_reason(
    home_state: Optional[str],
    program_state: Optional[str],
    max_tuition: Optional[float],
    program_tuition: Optional[float],
) -> str:
    parts: List[str] = []

    if home_state and program_state:
        if program_state == home_state:
            parts.append(
                "Located in your home state, which may make it more convenient and potentially more affordable."
            )
        else:
            parts.append(
                f"Located in {program_state}, outside your home state of {home_state}."
            )

    if isinstance(max_tuition, (int, float)) and max_tuition > 0:
        if isinstance(program_tuition, (int, float)):
            if program_tuition <= max_tuition:
                parts.append(
                    f"Estimated tuition (~${program_tuition:,.0f} per year) fits within your comfortable range."
                )
            else:
                parts.append(
                    f"Estimated tuition (~${program_tuition:,.0f} per year) is above your stated comfort level."
                )
        else:
            parts.append(
                "Tuition information is not available for this program, so we cannot compare it to your budget."
            )

    if not parts:
        return "A practical option to explore based on your broad preferences."

    return " ".join(parts)


# ---------------------------------------------------------------------------
# v10 Filtering logic – strict adherence to user preferences
# ---------------------------------------------------------------------------

def filter_programs_for_profile(
    profile: Dict[str, Any],
    programs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Apply hard filters based directly on Tab 1 preferences.

    Hard constraints:
      - At least one interest area selected: program must intersect with those.
      - At least one degree level selected: program.degree_level must be one of them.
      - If max_tuition > 0:
          - program must have numeric tuition
          - tuition must be <= max_tuition.
      - If location_pref == "instate" and home_state provided:
          program.state must equal home_state.
    """
    degree_pref = set(profile.get("degree_levels") or [])
    interests_pref = set(profile.get("interest_areas") or [])
    home_state = profile.get("home_state") or None

    max_tuition = profile.get("max_tuition")
    if isinstance(max_tuition, (int, float)) and max_tuition <= 0:
        max_tuition = None

    location_pref = (profile.get("location_pref") or "").lower()

    eligible: List[Dict[str, Any]] = []

    for p in programs:
        # Degree level match
        p_degree = (p.get("degree_level") or "").strip()
        if degree_pref and p_degree not in degree_pref:
            continue

        # Interest areas match (intersection must be non-empty)
        p_interests = set(p.get("interest_areas") or [])
        if interests_pref and not (p_interests & interests_pref):
            continue

        # Max tuition constraint (if user specified)
        tuition = p.get("annual_tuition")
        if isinstance(max_tuition, (int, float)) and max_tuition > 0:
            # For exact adherence: if tuition is unknown, we cannot assert it is <= max → exclude
            if not isinstance(tuition, (int, float)):
                continue
            if tuition > max_tuition:
                continue

        # Location preference
        p_state = p.get("state") or None
        if location_pref == "instate" and home_state:
            if not p_state or p_state != home_state:
                continue

        eligible.append(p)

    return eligible


# ---------------------------------------------------------------------------
# v10 Ranking logic – simple fit score for ordering (no safety buckets)
# ---------------------------------------------------------------------------

def rank_programs(
    profile: Dict[str, Any],
    programs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Compute a fit_score used only for ordering, not for eligibility.

    Components:
      - Interest overlap (up to INTEREST_WEIGHT)
      - Degree match (up to DEGREE_WEIGHT)
      - Location preference alignment (up to LOCATION_WEIGHT)
    """
    interests_pref = set(profile.get("interest_areas") or [])
    degree_pref = set(profile.get("degree_levels") or [])
    home_state = profile.get("home_state") or None
    location_pref = (profile.get("location_pref") or "").lower()

    ranked: List[Dict[str, Any]] = []

    for p in programs:
        p_interests = set(p.get("interest_areas") or [])
        p_degree = (p.get("degree_level") or "").strip()
        p_state = p.get("state") or None

        # Interest component
        overlap = interests_pref & p_interests
        if interests_pref:
            ratio = len(overlap) / len(interests_pref)
            interest_score = INTEREST_WEIGHT * ratio
        else:
            interest_score = 0.0

        # Degree component
        degree_score = DEGREE_WEIGHT if p_degree in degree_pref else 0.0

        # Location component
        location_score = 0.0
        if not location_pref:
            # Slight default preference score
            location_score = LOCATION_WEIGHT / 2
        elif location_pref == "instate":
            # Already filtered to in-state; give full score
            location_score = LOCATION_WEIGHT
        else:
            if home_state and p_state:
                location_score = (
                    LOCATION_WEIGHT
                    if p_state == home_state
                    else LOCATION_WEIGHT * 0.6
                )
            else:
                location_score = LOCATION_WEIGHT * 0.6

        raw_total = interest_score + degree_score + location_score

        enriched = dict(p)
        enriched.update(
            {
                "interest_score_component": round(interest_score, 1),
                "degree_score_component": round(degree_score, 1),
                "location_score_component": round(location_score, 1),
                "raw_total": raw_total,
            }
        )
        ranked.append(enriched)

    if not ranked:
        return []

    max_raw = max(p["raw_total"] for p in ranked) or 1.0

    for p in ranked:
        p["fit_score"] = int(round((p["raw_total"] / max_raw) * 100))

    # Sort by fit descending, then tuition ascending, then program name
    def _sort_key(x: Dict[str, Any]):
        tuition_val = x.get("annual_tuition")
        try:
            tuition_sort = (
                float(tuition_val)
                if tuition_val not in (None, "")
                else float("inf")
            )
        except (TypeError, ValueError):
            tuition_sort = float("inf")
        return (-x["fit_score"], tuition_sort, x.get("program_name") or "")

    ranked.sort(key=_sort_key)
    return ranked


def build_explanations(
    profile: Dict[str, Any],
    programs: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Attach human-readable 'why' explanations to each ranked program.
    """
    interests_pref = set(profile.get("interest_areas") or [])
    home_state = profile.get("home_state") or None
    max_tuition = profile.get("max_tuition")

    try:
        gpa = float(profile.get("gpa") or 0.0)
    except (TypeError, ValueError):
        gpa = 0.0

    enriched: List[Dict[str, Any]] = []

    for p in programs:
        p_interests = set(p.get("interest_areas") or [])
        p_state = p.get("state") or None
        p_tuition = p.get("annual_tuition")
        p_selectivity = p.get("selectivity_band")

        p_copy = dict(p)
        p_copy["why_interests"] = _build_interests_reason(
            interests_pref, p_interests
        )
        p_copy["why_academic"] = _build_academic_reason(
            gpa, p_selectivity
        )
        p_copy["why_practical"] = _build_practical_reason(
            home_state, p_state, max_tuition, p_tuition
        )
        enriched.append(p_copy)

    return enriched


# ---------------------------------------------------------------------------
# Profile builder (form → profile dict) and summaries
# ---------------------------------------------------------------------------

def build_profile_from_form(form) -> Dict[str, Any]:
    """
    Convert incoming form fields into a normalized profile dict (v10).
    """
    get = form.get
    getlist = form.getlist

    role = get("role") or ""
    current_status = get("current_status") or ""
    home_state = get("home_state") or ""
    gpa_raw = get("gpa") or ""

    try:
        gpa = float(gpa_raw) if gpa_raw != "" else 0.0
    except (TypeError, ValueError):
        gpa = 0.0

    degree_levels = [v for v in getlist("degree_levels") if v]
    interest_areas = [v for v in getlist("interest_areas") if v]

    max_tuition_raw = get("max_tuition") or ""
    sat_raw = get("sat_score") or ""
    act_raw = get("act_score") or ""
    location_pref = get("location_pref") or ""

    try:
        max_tuition = float(max_tuition_raw) if max_tuition_raw != "" else None
    except (TypeError, ValueError):
        max_tuition = None

    try:
        sat_score = int(sat_raw) if sat_raw != "" else None
    except (TypeError, ValueError):
        sat_score = None

    try:
        act_score = int(act_raw) if act_raw != "" else None
    except (TypeError, ValueError):
        act_score = None

    profile: Dict[str, Any] = {
        "role": role,
        "current_status": current_status,
        "home_state": home_state,
        "gpa": gpa,
        "degree_levels": degree_levels,
        "interest_areas": interest_areas,
        "max_tuition": max_tuition,
        "sat_score": sat_score,
        "act_score": act_score,
        "location_pref": location_pref,
    }
    return profile


def summarize_profile(profile: Optional[Dict[str, Any]]) -> str:
    """
    Build a short human-readable summary for the Recommendations tab header.
    """
    if not profile:
        return ""

    parts: List[str] = []

    role = (profile.get("role") or "").lower()
    if role == "student":
        parts.append("Student")
    elif role == "parent":
        parts.append("Parent")

    home_state = profile.get("home_state")
    if home_state:
        if parts:
            parts[-1] = f"{parts[-1]} from {home_state}"
        else:
            parts.append(f"From {home_state}")

    gpa = profile.get("gpa")
    try:
        gpa_val = float(gpa)
        if gpa_val > 0:
            parts.append(f"GPA {gpa_val:.1f}")
    except (TypeError, ValueError):
        pass

    degree_levels = profile.get("degree_levels") or []
    if degree_levels:
        parts.append(", ".join(degree_levels))

    interests = profile.get("interest_areas") or []
    if interests:
        parts.append(", ".join(interests))

    max_tuition = profile.get("max_tuition")
    if isinstance(max_tuition, (int, float)) and max_tuition > 0:
        parts.append(f"Max tuition ~${max_tuition:,.0f}/year")

    return " · ".join(parts)


def summarize_constraints(profile: Optional[Dict[str, Any]]) -> str:
    """
    Explicit summary of hard constraints applied in filtering.
    """
    if not profile:
        return ""

    parts: List[str] = []

    degree_levels = profile.get("degree_levels") or []
    interests = profile.get("interest_areas") or []
    max_tuition = profile.get("max_tuition")
    home_state = profile.get("home_state")
    location_pref = (profile.get("location_pref") or "").lower()

    if degree_levels:
        parts.append("Degree: " + ", ".join(degree_levels))

    if interests:
        parts.append("Interests: " + ", ".join(interests))

    if isinstance(max_tuition, (int, float)) and max_tuition > 0:
        parts.append(f"Tuition ≤ ${max_tuition:,.0f}/year")

    if location_pref == "instate" and home_state:
        parts.append(f"In-state only ({home_state})")
    elif location_pref == "out_of_state_ok":
        parts.append("In-state or out-of-state")
    elif location_pref == "anywhere":
        parts.append("Anywhere in the U.S.")

    return " · ".join(parts)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    programs = load_programs()
    data_error = len(programs) == 0

    profile: Optional[Dict[str, Any]] = None
    recommendations: List[Dict[str, Any]] = []
    active_tab = "profile"

    if request.method == "POST":
        profile = build_profile_from_form(request.form)
        session["v10_profile"] = profile

        if not data_error:
            eligible = filter_programs_for_profile(profile, programs)
            ranked = rank_programs(profile, eligible)
            recommendations = build_explanations(profile, ranked)

        active_tab = "recommendations"
    else:
        profile = session.get("v10_profile")
        if profile and not data_error:
            eligible = filter_programs_for_profile(profile, programs)
            ranked = rank_programs(profile, eligible)
            recommendations = build_explanations(profile, ranked)
        active_tab = "profile"

    profile_summary = summarize_profile(profile)
    constraints_summary = summarize_constraints(profile)

    return render_template(
        "index_v10.html",
        app_name=APP_NAME,
        profile=profile,
        profile_summary=profile_summary,
        constraints_summary=constraints_summary,
        recommendations=recommendations,
        active_tab=active_tab,
        data_error=data_error,
        degree_options=DEGREE_OPTIONS,
        interest_options=INTEREST_OPTIONS,
        us_states=US_STATES,
        INTEREST_WEIGHT=INTEREST_WEIGHT,
        DEGREE_WEIGHT=DEGREE_WEIGHT,
        LOCATION_WEIGHT=LOCATION_WEIGHT,
    )


if __name__ == "__main__":
    # For local demo
    app.run(host="0.0.0.0", port=5000, debug=True)
