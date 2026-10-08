// Waste Scanner & Auditing Workflow

let currentPrediction = null;
let selectedActualBin = null;

function initScanner() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("waste-file-input");
  const scanBtn = document.getElementById("scan-btn");

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("hover");
  });

  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("hover"));

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("hover");
    if (e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  // Load locations into audit dropdown
  loadLocationsDropdown();
}

async function loadLocationsDropdown() {
  try {
    const locs = await API.getCampusLocations();
    const select = document.getElementById("audit-location-select");
    if (select) {
      select.innerHTML = locs.map(l => `<option value="${l.id}">${l.name}</option>`).join("");
    }
  } catch (err) {
    console.error("Error loading locations:", err);
  }
}

function handleFileSelected(file) {
  const preview = document.getElementById("scanner-preview");
  const previewBox = document.getElementById("preview-container");
  const reader = new FileReader();

  reader.onload = (e) => {
    preview.src = e.target.result;
    previewBox.style.display = "flex";
  };
  reader.readAsDataURL(file);

  // Trigger classification
  classifyImage(file);
}

async function classifyImage(file) {
  const loading = document.getElementById("scanner-loading");
  const resultBox = document.getElementById("scanner-result");
  const auditSection = document.getElementById("audit-section");
  const thresholdVal = parseFloat(document.getElementById("confidence-threshold-input")?.value || "0.70");

  loading.style.display = "block";
  resultBox.style.display = "none";
  auditSection.style.display = "none";

  try {
    const res = await API.predictWaste(file, thresholdVal, true);
    currentPrediction = res;

    // Populate Results
    document.getElementById("res-waste-type").textContent = res.waste_class.toUpperCase();
    document.getElementById("res-category").textContent = res.waste_category;
    document.getElementById("res-confidence").textContent = `${(res.confidence * 100).toFixed(1)}%`;
    document.getElementById("res-latency").textContent = `${res.inference_time_ms} ms`;
    document.getElementById("res-model-name").textContent = res.model_name;

    const confBar = document.getElementById("res-conf-bar");
    confBar.style.width = `${res.confidence * 100}%`;

    // Low confidence warning
    const warnBox = document.getElementById("low-conf-warning");
    if (!res.is_confident) {
      warnBox.textContent = res.warning || "⚠ Low confidence classification. Please inspect carefully.";
      warnBox.style.display = "block";
    } else {
      warnBox.style.display = "none";
    }

    // Recommended bin card
    const binBox = document.getElementById("res-bin-box");
    const binName = document.getElementById("res-bin-name");
    binName.textContent = res.recommended_bin;

    if (res.recommended_bin.includes("Blue")) {
      binBox.style.backgroundColor = "rgba(59, 130, 246, 0.15)";
      binBox.style.border = "1px solid #3b82f6";
      binName.style.color = "#3b82f6";
    } else if (res.recommended_bin.includes("Green")) {
      binBox.style.backgroundColor = "rgba(16, 185, 129, 0.15)";
      binBox.style.border = "1px solid #10b981";
      binName.style.color = "#10b981";
    } else {
      binBox.style.backgroundColor = "rgba(239, 68, 68, 0.15)";
      binBox.style.border = "1px solid #ef4444";
      binName.style.color = "#ef4444";
    }

    // Grad-CAM Heatmap
    const gradBox = document.getElementById("gradcam-container");
    const gradImg = document.getElementById("gradcam-img");
    if (res.explainability_url) {
      gradImg.src = res.explainability_url;
      gradBox.style.display = "block";
    } else {
      gradBox.style.display = "none";
    }

    // Show result & audit sections
    resultBox.style.display = "block";
    auditSection.style.display = "block";

    // Pre-select recommended bin by default
    selectActualBin(res.recommended_bin);

  } catch (err) {
    showToast(`Inference failed: ${err.message}`, "error");
  } finally {
    loading.style.display = "none";
  }
}

function selectActualBin(binName) {
  selectedActualBin = binName;
  document.querySelectorAll(".bin-choice-btn").forEach(btn => {
    btn.classList.toggle("selected", btn.dataset.bin === binName);
  });
}

async function submitAuditConfirmation() {
  if (!currentPrediction || !selectedActualBin) {
    showToast("Please classify an image and select the actual bin.", "warning");
    return;
  }

  const locationId = parseInt(document.getElementById("audit-location-select").value);
  const auditData = {
    waste_class: currentPrediction.waste_class,
    actual_bin: selectedActualBin,
    confidence: currentPrediction.confidence,
    location_id: locationId,
    bin_id: "BIN-001",
    model_name: currentPrediction.model_name,
    model_version: currentPrediction.model_version,
    response_time_ms: currentPrediction.inference_time_ms
  };

  try {
    const res = await API.recordAudit(auditData);
    
    // Display outcome modal/panel
    const outcomeBox = document.getElementById("audit-outcome");
    outcomeBox.style.display = "block";

    if (res.segregation_status === "CORRECT") {
      outcomeBox.className = "card status-CORRECT";
      outcomeBox.innerHTML = `
        <div style="display:flex; align-items:center; gap:10px;">
          <span style="font-size:24px;">✅</span>
          <div>
            <strong>CORRECT SEGREGATION AUDITED</strong>
            <p style="font-size:0.85rem; margin-top:2px;">
              Item <em>${res.waste_class}</em> correctly placed into <strong>${res.actual_bin}</strong>.
              Audit record #${res.id} stored in database.
            </p>
          </div>
        </div>
      `;
      showToast("Audit recorded: Correct Segregation!", "success");
    } else if (res.segregation_status === "INCORRECT") {
      outcomeBox.className = "card status-INCORRECT";
      outcomeBox.innerHTML = `
        <div style="display:flex; align-items:center; gap:10px;">
          <span style="font-size:24px;">❌</span>
          <div>
            <strong>INCORRECT SEGREGATION / CONTAMINATION DETECTED</strong>
            <p style="font-size:0.85rem; margin-top:2px;">
              Item <em>${res.waste_class}</em> should have gone into <strong>${res.expected_bin}</strong>, 
              but was deposited in <strong>${res.actual_bin}</strong>. Contamination recorded!
            </p>
          </div>
        </div>
      `;
      showToast("Contamination logged: Incorrect bin used", "warning");
    } else {
      outcomeBox.className = "card status-UNCERTAIN";
      outcomeBox.innerHTML = `
        <div style="display:flex; align-items:center; gap:10px;">
          <span style="font-size:24px;">⚠️</span>
          <div>
            <strong>UNCERTAIN CLASSIFICATION RECORDED</strong>
            <p style="font-size:0.85rem; margin-top:2px;">
              Low confidence audit saved for secondary human verification.
            </p>
          </div>
        </div>
      `;
    }

    // Refresh overview KPIs and recent audits table
    if (window.refreshOverviewData) window.refreshOverviewData();

  } catch (err) {
    showToast(`Failed to record audit: ${err.message}`, "error");
  }
}

// User Feedback handler
async function submitFeedbackRating(rating) {
  const commentInput = document.getElementById("feedback-comment");
  const comment = commentInput ? commentInput.value : "";
  try {
    await API.submitFeedback({
      rating: rating,
      feedback_type: "RECOMMENDATION_USEFULNESS",
      comments: comment
    });
    showToast(`Thank you! Rated ${rating} stars.`, "success");
    document.getElementById("feedback-modal").style.display = "none";
  } catch (err) {
    showToast(`Feedback error: ${err.message}`, "error");
  }
}
