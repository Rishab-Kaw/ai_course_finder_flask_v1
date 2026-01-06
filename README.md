

---

# AI Course Finder – v10

*Find the perfect college program based on your unique profile*

## 1. Overview

**AI Course Finder – v10** is a lightweight Flask web application that helps students and parents discover U.S. college programs that align with:

* Academic profile (GPA, optional test scores)
* Desired degree level
* Interest areas (e.g., Engineering, Computer Science, Business, Healthcare, Arts)
* Budget (maximum affordable annual tuition)
* Study location preference (in-state vs anywhere in the U.S.)

It is designed as a **demo-quality product**: visually polished and interactive on the frontend, with a clear, maintainable backend that uses a **static JSON dataset** (`programs_v7.json`) to simulate realistic program data.

Key design principles:

* **Simple architecture**: One file per type – 1 Python backend, 1 HTML template, 1 CSS, 1 JS, 1 JSON.
* **Desktop-first UX** with Bootstrap styling.
* **Deterministic recommendation logic** that strictly honors user preferences.
* **No over-engineering**: everything is explicit and easy to read / modify.

---

## 2. Tech Stack and File Layout

### 2.1. Tech Stack

* **Backend**: Python, Flask
* **Frontend**: HTML, Bootstrap 5, vanilla JavaScript
* **Styling**: Custom CSS (light, colorful theme)
* **Data**: Static JSON file (`programs_v7.json`)

### 2.2. File Layout

All files live in a **single folder** (no nested app structure):

* `app_v10.py`
  Flask application (routes, recommendation engine, scoring, explanations).

* `index_v10.html`
  Main HTML template for the entire UI (tabs, forms, cards, modals).

* `style_v10.css`
  Custom CSS stylesheet (layout, theme, cards, chips, progress bar, etc.).

* `main_v10.js`
  Frontend behavior: form completeness, sliders, Quick Fill, filters, sorting, modal details.

* `programs_v7.json`
  Demo dataset of college programs and institutions used by v10.

All are expected to be in the **same directory** for v10 to work.

---

## 3. Installation and Setup

### 3.1. Prerequisites

* **Python** 3.8+ (3.10/3.11/3.12+ all fine)
* Internet access (only for serving Bootstrap from CDN; optional if you host Bootstrap locally)
* `pip` package manager

### 3.2. Install Dependencies

Create a virtual environment if you prefer, then install Flask:

```bash
pip install flask
```

No other external Python packages are required.

### 3.3. Place Files

Ensure the following files are in the same folder:

```text
app_v10.py
index_v10.html
style_v10.css
main_v10.js
programs_v7.json
```

### 3.4. Optional: Secret Key Configuration

By default, the app uses a hard-coded development secret key.
You can override it using an environment variable:

* Environment variable: `COURSE_FINDER_V10_SECRET_KEY`

Example (Windows PowerShell):

```powershell
$env:COURSE_FINDER_V10_SECRET_KEY = "some-long-random-string"
python app_v10.py
```

Example (Linux/macOS):

```bash
export COURSE_FINDER_V10_SECRET_KEY="some-long-random-string"
python app_v10.py
```

This secret key is used only for Flask sessions (to remember the last profile).

---

## 4. Running the Application

From the folder containing `app_v10.py`, run:

```bash
python app_v10.py
```

The default Flask development server will start on:

* `http://0.0.0.0:5000` (or `http://localhost:5000`)

Open this URL in your browser to use the app.

---

## 5. Data Model – `programs_v7.json`

### 5.1. Structure

`programs_v7.json` is a list of program objects. Each object typically contains fields like:

```json
{
  "program_id": "uic_cs_bs",
  "program_name": "B.S. in Computer Science",
  "institution_name": "University of Illinois Chicago",
  "state": "IL",
  "city": "Chicago",
  "degree_level": "Bachelor's",
  "interest_areas": ["Computer Science", "Engineering"],
  "annual_tuition": 18500,
  "selectivity_band": "selective",
  "median_salary_band": "$60,000–$70,000",
  "program_snippet": "Strong ABET-accredited CS program with solid placement in tech and industry.",
  "delivery_modes": ["On-Campus"]
}
```

Key fields used by v10:

* `program_id` (string): Unique ID for the program (used on cards and modals).
* `program_name` (string): Name of the program.
* `institution_name` (string): College/university name.
* `state` (string): 2-letter US state code.
* `city` (string, optional): City of the campus.
* `degree_level` (string):
  Expected to be one of:

  * `"Certificate"`, `"Associate"`, `"Bachelor's"`
    (These correspond exactly to the options shown in the UI.)
* `interest_areas` (array of strings):
  Contains one or more interest tags, e.g. `"Engineering"`, `"Computer Science"`, `"Business"`, `"Healthcare"`, `"Arts"`.
* `annual_tuition` (number or null):
  Approximate annual tuition in USD. Parsed as a float by the backend.
* `selectivity_band` (string, optional):
  One of `"highly_selective"`, `"selective"`, `"moderate"`, `"open"` or blank; used only for academic explanation text.
* `median_salary_band` (string, optional):
  Short descriptor of early-career earnings (purely informational).
* `program_snippet` (string, optional):
  Short description for the card.

### 5.2. Normalization

The backend normalizes:

* `annual_tuition` to `float` or `None`.
* `interest_areas` and `delivery_modes` so they are always lists (never a string or null).

---

## 6. Frontend UX – Tabs and Flows

The app has two main tabs:

1. **Tab 1 – “Your Profile and Preferences”**
2. **Tab 2 – “Your Personalized Recommendations”**

A step indicator at the top visually marks progress between these two steps.

### 6.1. Global UI Elements

* **App title**: “AI Course Finder”
* **Byline**: “Find the perfect college program based on your unique profile”
* **Top-right buttons**:

  * `Quick Fill (Demo Persona)`
  * `Clear Form`
* **Profile completeness bar**:

  * Shows 0–100% completeness based on required fields.
  * The **Generate Recommendations** button is disabled until profile completeness reaches 100%.

---

## 7. Tab 1: Your Profile and Preferences

Tab 1 contains an accordion with four sections.

### 7.1. Required vs Optional Fields

**Required (to enable Generate button):**

1. Role: Student / Parent (radio)
2. Current Status: High school student / High school graduate
3. Home State (US state dropdown)
4. High School GPA (slider > 0)
5. At least one Degree Level
6. At least one Interest Area

**Optional:**

* SAT score
* ACT score
* Max tuition (can be left as 0 or cleared, meaning “no hard budget filter”)
* Location preference (can be left blank, meaning “no strict location constraint”)

### 7.2. Section 1: Basic Profile

* **Are you a Student or Parent?**

  * Radio buttons: `Student`, `Parent`.
* **Current Status**

  * Dropdown:

    * High school student
    * High school graduate
* **Home State**

  * Dropdown of all 50 U.S. states (2-letter codes).

### 7.3. Section 2: Academic Profile

* **High School GPA**

  * Slider: `0.0` to `4.0` (step `0.1`).
  * Linked numeric input: GPA value shown and editable.
* **SAT Score** (optional)

  * Numeric input: allowed range `400–1600`.
* **ACT Score** (optional)

  * Numeric input: allowed range `1–36`.

GPA is used for **academic context explanations**, not for filtering or “safety” categorization.

### 7.4. Section 3: Education Level & Interests

* **Degree Levels you are considering** (multi-select via checkboxes):

  * Certificate
  * Associate
  * Bachelor’s
* **Interest Areas** (multi-select via checkboxes):

  * Engineering
  * Computer Science
  * Business
  * Healthcare
  * Arts

A program is considered only if:

* Its `degree_level` matches one of the checked degree levels.
* Its `interest_areas` array has at least one overlap with the selected interest areas.

### 7.5. Section 4: Budget & Location

* **Max comfortable annual tuition (USD)**

  * Slider: 5,000 to 80,000, step 1,000.
  * Numeric input: linked to the slider; can be set to 0 or left blank to effectively remove the hard budget constraint.
* **Study location preference**

  * Dropdown options (after your latest adjustment):

    * `In-state only`
    * `Anywhere in the U.S.`

Behavior:

* If `In-state only` is chosen and **Home State** is set:

  * Only programs whose `state` equals the user’s home state are considered.
* If `Anywhere in the U.S.` is chosen:

  * No location filter is applied.
* If left blank:

  * Location is not used as a hard constraint; only used as a softer ranking component.

### 7.6. Generate Recommendations button

* Label: **Generate Recommendations**
* Type: `submit` (posts form to `/`).
* Disabled until **all required fields** are filled (100% profile completeness).

---

## 8. Tab 2: Your Personalized Recommendations

Tab 2 shows a two-column layout:

* **Left (sidebar)** – Quick Filters
* **Right (main area)** – Program recommendation cards

### 8.1. Header

* Text: “Recommendations”
* `X matches` where X is the number of programs currently visible after backend + frontend filters.
* Sort dropdown: `Sort by`:

  * `Best overall fit` (default)
  * `Lowest tuition first`
  * `Highest tuition first`
* On the right: **constraints summary chip**, e.g.:

> Degree: Bachelor’s · Interests: Engineering, Computer Science · Tuition ≤ $25,000/year · In-state only (IL)

This is built from the user’s Tab 1 selections.

### 8.2. Left Sidebar – Quick Filters

Card labeled **Quick Filters** with:

1. **Degree level** filter:

   * All
   * Certificate
   * Associate
   * Bachelor’s
     (Filters only on the frontend, on top of the backend’s existing constraints.)
2. **Max tuition (USD)** filter:

   * Numeric input.
   * If set, hides cards with tuition strictly above this value (cards with no tuition value remain visible unless backend has already excluded them via the main budget constraint).

These filters are applied purely on the client via `main_v10.js`.

### 8.3. Right Main Area – Program Cards

Each recommendation is shown as a **single-column card** (no multi-column grid), with:

* **Title**: Program name (e.g. “B.S. in Computer Science”)
* **Subtitle**: Institution name and state (e.g. “University of Illinois Chicago · IL”)
* **Interest chips**:

  * One chip per `interest_areas` entry.
  * Chips that match user-selected interests are visually highlighted.
* **Optional snippet**: `program_snippet` shown as a short description.

#### Fit score and dimensions

* Badge: `Fit score: N/100`
* Three “fit dimensions” with bar graphics:

  * Interests
  * Degree
  * Location

These bars correspond to internal scoring components:

* Interests (up to 70 points)
* Degree (up to 20 points)
* Location (up to 10 points)

Normalized so that total `fit_score` is scaled 0–100 across all eligible programs.

#### Tuition, degree level, and salary band

* **Tuition (est.)**:

  * `$XX,XXX/year` or `Not available` if tuition is missing.
* **Degree level**: e.g. `Bachelor's`.
* **Typical early-career earnings**:

  * Shown if `median_salary_band` is present in JSON.

#### Why this recommendation? (Explanations)

Each card shows:

* **Why this recommendation?**

and then three lines:

1. `why_interests` – explains interest match
   e.g. “Matches your interest areas: Engineering, Computer Science.”
2. `why_academic` – explains academic context
   based on user GPA and `selectivity_band`.
   e.g. “Your GPA is roughly in line with the typical range for this school…”
3. `why_practical` – explains location + budget practicality
   e.g. “Located in your home state… Estimated tuition fits within your comfortable range.”

#### View details modal

Button: **View more details**

* Opens a Bootstrap modal with:

  * Program title
  * Institution and location
  * Fit score
  * Degree level
  * Tuition
  * The same three explanations:

    * Interests
    * Academic context
    * Practical considerations

The modal is fully populated on the client side using `data-*` attributes and DOM text.

---

## 9. Recommendation Engine – Backend Logic

The core pipeline is implemented in **`app_v10.py`**.

### 9.1. Data Loading – `load_programs()`

* Loads `programs_v7.json` into memory once and caches it.
* Normalizes:

  * `annual_tuition` → float or `None`.
  * `interest_areas`, `delivery_modes` → lists.
* If the file is missing or invalid:

  * `data_error = True` and Tab 2 shows a warning alert.

### 9.2. Profile Building – `build_profile_from_form()`

For a submitted POST form, the function builds a `profile` dictionary:

```python
profile = {
    "role": "student" or "parent",
    "current_status": "high_school_student" or "high_school_graduate",
    "home_state": "IL" (etc.),
    "gpa": float,  # 0.0 if parse fails
    "degree_levels": [ "Bachelor's", ... ],
    "interest_areas": [ "Engineering", "Computer Science", ... ],
    "max_tuition": float or None,
    "sat_score": int or None,
    "act_score": int or None,
    "location_pref": "instate", "anywhere", or ""
}
```

This profile is stored in the Flask `session` so that, on subsequent GET requests, the app can automatically re-generate recommendations without re-submitting the form.

### 9.3. Filtering – `filter_programs_for_profile()`

This function applies **hard constraints** based exactly on Tab 1 preferences:

1. **Degree level**:

   * `program.degree_level` must be in `profile["degree_levels"]`.
2. **Interest areas**:

   * `set(program.interest_areas) ∩ set(profile["interest_areas"])` must be non-empty.
3. **Max tuition**:

   * If `profile["max_tuition"]` is a positive number:

     * The program must have a **numeric** `annual_tuition`.
     * `annual_tuition <= max_tuition`.
     * Programs with missing tuition are excluded when a max is specified.
4. **Location preference**:

   * If `location_pref == "instate"` and `home_state` provided:

     * `program.state` must exactly match `home_state`.
   * If `location_pref == "anywhere"` or blank:

     * No hard location filter; location only influences the score slightly.

The output is a list of **eligible programs**. Programs that do not meet all these constraints are **not shown at all**.

### 9.4. Scoring and Ranking – `rank_programs()`

For each eligible program, a **fit score** is computed as a weighted sum of three components:

1. **Interest score** (`INTEREST_WEIGHT` = 70.0)

   * Proportion of selected interests that overlap with the program’s interests.
   * `interest_score = INTEREST_WEIGHT * (overlap_count / selected_interests_count)`
2. **Degree score** (`DEGREE_WEIGHT` = 20.0)

   * Either 0 or full 20:

     * 20 if `program.degree_level` is in selected degree levels.
3. **Location score** (`LOCATION_WEIGHT` = 10.0)

   * Reflects rough alignment with location preference:

     * If `location_pref == "instate"`: full 10 (since the filter already enforced in-state).
     * If blank or `"anywhere"`:

       * If home_state and program state are known, program in home_state gets slightly higher score than others.
       * Otherwise, a moderate default score is given.

The raw sum of these components is normalized:

* Find `max_raw` among eligible programs.
* Each program gets:

  * `fit_score = round((raw_total / max_raw) * 100)`

The final sort order for backend output is:

1. `fit_score` descending
2. `annual_tuition` ascending (unknown tuition treated as +∞)
3. `program_name` alphabetical

### 9.5. Explanations – `build_explanations()`

This function enriches each ranked program with:

* `why_interests` – textual explanation for interest match.
* `why_academic` – explanation for GPA vs selectivity.
* `why_practical` – explanation for budget and home-state interplay.

All explanations are descriptive. There are **no “Safer / Realistic / Reach”** labels in v10.

### 9.6. Profile and Constraint Summaries

* `summarize_profile(profile)`:

  * Builds a short tagline like:

    > Student from IL · GPA 3.6 · Bachelor's · Engineering, Computer Science · Max tuition ~$25,000/year
* `summarize_constraints(profile)`:

  * Used in Tab 2’s constraints chip:

    > Degree: Bachelor's · Interests: Engineering, Computer Science · Tuition ≤ $25,000/year · In-state only (IL)

---

## 10. Frontend Behavior – `main_v10.js`

Key responsibilities:

1. **Profile completeness tracking**

   * Watches required fields:

     * `role`, `current_status`, `home_state`, `gpa`, at least one `degree_levels`, at least one `interest_areas`.
   * Updates:

     * Progress bar (% complete)
     * Label text (“X% complete”)
     * Generate button enabled/disabled.
   * Shows a hint under the completeness bar.

2. **GPA slider ↔ numeric input sync**

   * Slider and numeric field stay in sync.
   * Clamps GPA to `[0, 4]`.

3. **Max tuition slider ↔ numeric input sync**

   * Slider and numeric input remain consistent.
   * Clamps tuition to `[0, 80,000]`.

4. **Quick Fill (Demo Persona)**

   * Sets:

     * Role = Student
     * Status = High school student
     * Home state = IL
     * GPA ≈ 3.6
     * Max tuition ≈ 25,000
     * Degree = Bachelor’s
     * Interests = Engineering + Computer Science
   * Updates completeness bar.
   * Shows a small Bootstrap toast: “Demo persona applied…”

5. **Clear Form**

   * Resets all fields and checkboxes.
   * Resets GPA & tuition to default values (3.0 and 25,000).
   * Clears SAT/ACT.
   * Updates completeness back down.

6. **Quick Filters & Sorting (Tab 2)**

   * Filters by:

     * Degree level (select)
     * Max tuition (numeric input)
   * Sorting modes:

     * Best overall fit (uses `data-fit-score`)
     * Lowest tuition first
     * Highest tuition first
   * Updates visible card count (`X matches`) and DOM order of cards.

7. **Details Modal Population**

   * On `show.bs.modal`, uses the clicked card’s `data-program-id` to locate the card.
   * Extracts:

     * Title, institution line, fit score, degree, tuition.
     * `why_interests`, `why_academic`, `why_practical` text.
   * Injects these into modal elements.

---

## 11. Session Behavior

* The last submitted profile (`v10_profile`) is stored in Flask **session**.
* On a GET request:

  * If a profile is found in session and data is available:

    * The backend regenerates recommendations and pre-populates Tab 2.
    * Fields in Tab 1 are also pre-filled as much as possible.

This gives a “sticky” experience: users returning to the page see their last profile and recommendations without re-entering everything.

---

## 12. Validation, Requirements, and Error States

* **Required fields** are enforced on the frontend only (via completeness logic).
* Numeric parsing is **defensive**:

  * Invalid numbers are treated as 0 or `None` without crashing.
* Missing or invalid `programs_v7.json`:

  * Tab 2 shows a warning alert indicating that the dataset could not be loaded.
* Backend runs in `debug=True` mode by default for local development. For production-like scenarios, this should be turned off.

---

## 13. Customization and Extension

Some common customizations:

1. **Change the app name/branding**

   * Edit `APP_NAME` in `app_v10.py`.
   * Optionally update headings in `index_v10.html`.

2. **Add or change degree level options**

   * Update `DEGREE_OPTIONS` in `app_v10.py`.
   * Update the checkbox list in `index_v10.html`.
   * Ensure `programs_v7.json` uses the same strings.

3. **Add or change interest areas**

   * Update `INTEREST_OPTIONS` in `app_v10.py`.
   * Update checkboxes in `index_v10.html`.
   * Ensure `interest_areas` in JSON align.

4. **Adjust scoring weights**

   * Modify `INTEREST_WEIGHT`, `DEGREE_WEIGHT`, `LOCATION_WEIGHT` in `app_v10.py`.
   * These automatically propagate to fit-score calculations and bar widths (passed into the template).

5. **Change location behavior**

   * Modify `filter_programs_for_profile()` and `rank_programs()` for different in-state rules, or to reintroduce the “in-state or out-of-state” option if needed.

6. **Replace the dataset**

   * Provide a new `programs_v7.json` with the same schema.
   * The UI and logic will automatically use the new data.

---

## 14. Limitations and Intentional Simplifications

* **No Shortlist**:
  Earlier versions had a shortlist tab; v10 intentionally **removes** shortlist functionality for simplicity.
* **Static dataset**:
  All recommendations come from a local JSON file. There is no live connection to official data sources or APIs in v10.
* **No “safety” categories**:
  v10 does not compute or show Safer / Realistic / Reach labels. GPA and selectivity are used only for qualitative academic explanations.
* **Single-page app style, single route**:
  All functionality is served from `/` with GET + POST.

---

## 15. Summary

**AI Course Finder – v10** is a clean, production-style demo application that:

* Collects a structured student/parent profile.
* Enforces a clear set of constraints and filters.
* Ranks eligible programs with a transparent fit score.
* Explains the reasoning behind each recommendation.
* Keeps architecture simple: **one Python file, one HTML, one CSS, one JS, one JSON**.


