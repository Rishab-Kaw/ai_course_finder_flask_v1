/*
  AI Course Finder – v10
  Frontend behavior:
  - Profile completeness & required fields
  - GPA / tuition sliders
  - Quick Fill + Clear
  - Filters + sorting on recommendations
  - Details modal wiring
*/

document.addEventListener("DOMContentLoaded", () => {
  // ------------------------------------------------------------------------
  // DOM references
  // ------------------------------------------------------------------------
  const profileForm = document.getElementById("profile-form");
  const generateBtn = document.getElementById("btn-generate");
  const completenessBar = document.getElementById("profile-completeness-bar");
  const completenessLabel = document.getElementById("profile-completeness-label");
  const generateHint = document.getElementById("generate-hint");

  const gpaSlider = document.getElementById("gpa");
  const gpaValue = document.getElementById("gpa-value");

  const maxTuitionSlider = document.getElementById("max_tuition_slider");
  const maxTuitionInput = document.getElementById("max_tuition");

  const quickFillBtn = document.getElementById("btn-quick-fill");
  const clearFormBtn = document.getElementById("btn-clear-form");

  const filterDegree = document.getElementById("filter-degree");
  const filterMaxTuition = document.getElementById("filter-max-tuition");
  const sortBySelect = document.getElementById("sort-by");
  const cardsContainer = document.getElementById("recommendations-list");
  const resultCount = document.getElementById("result-count");

  // ------------------------------------------------------------------------
  // Required fields
  // Required: role, current_status, home_state, gpa, degree_levels, interest_areas
  // ------------------------------------------------------------------------
  function isRadioGroupFilled(name) {
    const nodes = document.querySelectorAll(`input[type="radio"][name="${name}"]`);
    return Array.from(nodes).some((n) => n.checked);
  }

  function isSelectFilled(id) {
    const el = document.getElementById(id);
    return !!el && !!el.value;
  }

  function isSliderFilled(id) {
    const el = document.getElementById(id);
    if (!el) return false;
    const v = parseFloat(el.value);
    return !Number.isNaN(v) && v > 0;
  }

  function isCheckboxGroupFilled(selector) {
    const nodes = document.querySelectorAll(selector);
    return Array.from(nodes).some((n) => n.checked);
  }

  function computeCompleteness() {
    let completedParts = 0;
    const totalParts = 6;

    if (isRadioGroupFilled("role")) completedParts++;
    if (isSelectFilled("current_status")) completedParts++;
    if (isSelectFilled("home_state")) completedParts++;
    if (isSliderFilled("gpa")) completedParts++;
    if (isCheckboxGroupFilled(".degree-level")) completedParts++;
    if (isCheckboxGroupFilled(".interest-area")) completedParts++;

    return Math.round((completedParts / totalParts) * 100);
  }

  function updateProfileCompleteness() {
    const pct = computeCompleteness();
    if (completenessBar) completenessBar.style.width = pct + "%";
    if (completenessLabel) completenessLabel.textContent = pct + "% complete";

    const complete = pct === 100;
    if (generateBtn) generateBtn.disabled = !complete;
    if (generateHint) {
      generateHint.textContent = complete
        ? "You’re ready to generate recommendations."
        : "Fill out the required fields to enable the Generate button.";
    }
  }

  // ------------------------------------------------------------------------
  // GPA + Max Tuition sliders
  // ------------------------------------------------------------------------
  if (gpaSlider && gpaValue) {
    gpaValue.value = gpaSlider.value;
    gpaSlider.addEventListener("input", () => {
      gpaValue.value = gpaSlider.value;
      updateProfileCompleteness();
    });
    gpaValue.addEventListener("change", () => {
      const v = parseFloat(gpaValue.value);
      if (!Number.isNaN(v)) {
        gpaSlider.value = Math.min(Math.max(v, 0), 4);
      }
      updateProfileCompleteness();
    });
  }

  if (maxTuitionSlider && maxTuitionInput) {
    maxTuitionSlider.addEventListener("input", () => {
      maxTuitionInput.value = maxTuitionSlider.value;
    });
    maxTuitionInput.addEventListener("change", () => {
      const v = parseFloat(maxTuitionInput.value);
      if (!Number.isNaN(v)) {
        const clamped = Math.min(Math.max(v, 0), 80000);
        maxTuitionInput.value = clamped;
        maxTuitionSlider.value = clamped;
      }
    });
  }

  // ------------------------------------------------------------------------
  // Quick Fill persona + Clear form
  // ------------------------------------------------------------------------
  function applyQuickFillPersona() {
    const roleStudent = document.getElementById("role-student");
    if (roleStudent) roleStudent.checked = true;

    const currentStatus = document.getElementById("current_status");
    if (currentStatus) currentStatus.value = "high_school_student";

    const homeState = document.getElementById("home_state");
    if (homeState) homeState.value = "IL";

    if (gpaSlider && gpaValue) {
      gpaSlider.value = "3.6";
      gpaValue.value = "3.6";
    }

    if (maxTuitionSlider && maxTuitionInput) {
      maxTuitionSlider.value = "25000";
      maxTuitionInput.value = "25000";
    }

    // Degree levels (Bachelor's)
    document.querySelectorAll(".degree-level").forEach((cb) => {
      cb.checked = cb.value === "Bachelor's";
    });

    // Interest areas (Engineering + Computer Science)
    document.querySelectorAll(".interest-area").forEach((cb) => {
      cb.checked =
        cb.value === "Engineering" || cb.value === "Computer Science";
    });

    updateProfileCompleteness();

    const toastEl = document.getElementById("quickFillToast");
    if (toastEl && window.bootstrap) {
      const toast = new bootstrap.Toast(toastEl);
      toast.show();
    }
  }

  function clearProfileForm() {
    if (!profileForm) return;
    profileForm.reset();

    ["current_status", "home_state", "location_pref"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.value = "";
    });

    document
      .querySelectorAll(".degree-level, .interest-area")
      .forEach((cb) => {
        cb.checked = false;
      });

    if (gpaSlider && gpaValue) {
      gpaSlider.value = "3.0";
      gpaValue.value = "3.0";
    }
    if (maxTuitionSlider && maxTuitionInput) {
      maxTuitionSlider.value = "25000";
      maxTuitionInput.value = "25000";
    }

    const satScore = document.querySelector("input[name='sat_score']");
    const actScore = document.querySelector("input[name='act_score']");
    if (satScore) satScore.value = "";
    if (actScore) actScore.value = "";

    updateProfileCompleteness();
  }

  if (quickFillBtn) {
    quickFillBtn.addEventListener("click", (e) => {
      e.preventDefault();
      applyQuickFillPersona();
    });
  }

  if (clearFormBtn) {
    clearFormBtn.addEventListener("click", (e) => {
      e.preventDefault();
      clearProfileForm();
    });
  }

  if (profileForm) {
    profileForm
      .querySelectorAll("input, select")
      .forEach((el) => el.addEventListener("change", updateProfileCompleteness));
  }
  updateProfileCompleteness();

  // ------------------------------------------------------------------------
  // Recommendations: filters & sorting
  // ------------------------------------------------------------------------
  function applyFiltersAndSort() {
    if (!cardsContainer) {
      if (resultCount) resultCount.textContent = "0";
      return;
    }
    const cards = Array.from(cardsContainer.querySelectorAll(".program-card"));
    if (!cards.length) {
      if (resultCount) resultCount.textContent = "0";
      return;
    }

    const deg = filterDegree ? filterDegree.value : "";
    const maxT = filterMaxTuition ? parseFloat(filterMaxTuition.value) : NaN;
    const sortBy = sortBySelect ? sortBySelect.value : "fit_desc";

    let visible = 0;

    cards.forEach((card) => {
      const cardDegree = card.dataset.degreeLevel || "";
      const cardTuition = parseFloat(card.dataset.tuition || "NaN");

      let show = true;

      if (deg && cardDegree !== deg) show = false;
      if (!Number.isNaN(maxT) && !Number.isNaN(cardTuition) && cardTuition > maxT)
        show = false;

      card.style.display = show ? "" : "none";
      if (show) visible++;
    });

    if (resultCount) {
      resultCount.textContent = String(visible);
    }

    // Sort all cards (visible + hidden) by chosen key
    const sorted = cards.slice().sort((a, b) => {
      const aFit = parseInt(a.dataset.fitScore || "0", 10);
      const bFit = parseInt(b.dataset.fitScore || "0", 10);
      const aTuition = parseFloat(a.dataset.tuition || "NaN");
      const bTuition = parseFloat(b.dataset.tuition || "NaN");

      if (sortBy === "fit_desc") {
        return bFit - aFit;
      }
      if (sortBy === "tuition_asc") {
        const aVal = Number.isNaN(aTuition) ? Number.POSITIVE_INFINITY : aTuition;
        const bVal = Number.isNaN(bTuition) ? Number.POSITIVE_INFINITY : bTuition;
        return aVal - bVal;
      }
      if (sortBy === "tuition_desc") {
        const aVal = Number.isNaN(aTuition) ? Number.NEGATIVE_INFINITY : aTuition;
        const bVal = Number.isNaN(bTuition) ? Number.NEGATIVE_INFINITY : bTuition;
        return bVal - aVal;
      }
      return 0;
    });

    sorted.forEach((card) => cardsContainer.appendChild(card));
  }

  [filterDegree, filterMaxTuition, sortBySelect].forEach((el) => {
    if (!el) return;
    el.addEventListener("change", applyFiltersAndSort);
    if (el === filterMaxTuition) {
      el.addEventListener("input", applyFiltersAndSort);
    }
  });

  applyFiltersAndSort();

  // ------------------------------------------------------------------------
  // Details modal
  // ------------------------------------------------------------------------
  const detailsModal = document.getElementById("detailsModal");
  if (detailsModal) {
    detailsModal.addEventListener("show.bs.modal", (event) => {
      const triggerBtn = event.relatedTarget;
      if (!triggerBtn) return;
      const programId = triggerBtn.getAttribute("data-program-id");
      if (!programId) return;

      const selector = `.program-card[data-program-id="${CSS.escape(programId)}"]`;
      const card = document.querySelector(selector);
      if (!card) return;

      const title = card.querySelector(".card-title")?.textContent || "";
      const institutionLine =
        card.querySelector(".text-muted.small")?.textContent || "";
      const fitScore = card.dataset.fitScore || "";
      const degreeLevel = card.dataset.degreeLevel || "";

      const tuition = (() => {
        const t = card.dataset.tuition;
        if (!t) return "Not available";
        const num = parseFloat(t);
        if (Number.isNaN(num)) return "Not available";
        return `$${num.toLocaleString("en-US", { maximumFractionDigits: 0 })}/year`;
      })();

      const whyBlocks = card.querySelectorAll(".mb-2.small.text-muted div");
      const whyInterests = whyBlocks[0]?.textContent || "";
      const whyAcademic = whyBlocks[1]?.textContent || "";
      const whyPractical = whyBlocks[2]?.textContent || "";

      document.getElementById("detailsModalTitle").textContent = title;
      document.getElementById("detailsModalInstitution").textContent =
        institutionLine;
      document.getElementById("detailsModalFitScore").textContent = fitScore
        ? `${fitScore}/100`
        : "";
      document.getElementById("detailsModalDegree").textContent = degreeLevel;
      document.getElementById("detailsModalTuition").textContent = tuition;
      document.getElementById("detailsModalWhyInterests").textContent =
        whyInterests;
      document.getElementById("detailsModalWhyAcademic").textContent =
        whyAcademic;
      document.getElementById("detailsModalWhyPractical").textContent =
        whyPractical;
    });
  }
});
