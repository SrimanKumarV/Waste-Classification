// Real-Time IoT Monitoring & Simulation Interface

let autoSimInterval = null;

async function loadIoTBins() {
  const container = document.getElementById("bins-grid-container");
  if (!container) return;

  try {
    const bins = await API.getBins();
    container.innerHTML = bins.map(b => renderBinCard(b)).join("");

    // Populate simulator select
    const simSelect = document.getElementById("sim-bin-select");
    if (simSelect && simSelect.options.length <= 1) {
      simSelect.innerHTML = bins.map(b => `<option value="${b.id}">${b.id} (${b.location_name} - ${b.bin_type})</option>`).join("");
    }
  } catch (err) {
    console.error("Error loading IoT bins:", err);
  }
}

function renderBinCard(b) {
  let statusColor = "var(--status-normal)";
  let barClass = "status-NORMAL";
  if (b.status === "CRITICAL") {
    statusColor = "var(--status-critical)";
    barClass = "status-CRITICAL";
  } else if (b.status === "HIGH") {
    statusColor = "var(--status-high)";
    barClass = "status-HIGH";
  } else if (b.status === "MODERATE") {
    statusColor = "var(--status-moderate)";
    barClass = "status-MODERATE";
  }

  return `
    <div class="bin-card" id="card-${b.id}">
      <div class="bin-header">
        <div>
          <strong style="font-size:1.1rem; color:#fff;">${b.id}</strong>
          <div style="font-size:0.75rem; color:var(--text-secondary);">${b.location_name}</div>
        </div>
        <span class="badge-status ${barClass}">${b.status}</span>
      </div>

      <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:4px;">${b.bin_type}</div>

      <div style="display:flex; justify-content:space-between; align-items:baseline; margin-top:6px;">
        <span style="font-size:1.7rem; font-weight:700; color:${statusColor};">${b.fill_percentage}%</span>
        <span style="font-size:0.8rem; color:var(--text-secondary);">Fill Level</span>
      </div>

      <div class="progress-bar-bg">
        <div class="progress-bar-fill" style="width:${b.fill_percentage}%; background-color:${statusColor};"></div>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-top:14px; padding-top:10px; border-top:1px solid var(--border-subtle); text-align:center;">
        <div>
          <div style="font-size:0.7rem; color:var(--text-muted);">WEIGHT</div>
          <div style="font-size:0.9rem; font-weight:600;">${b.weight_kg} kg</div>
        </div>
        <div>
          <div style="font-size:0.7rem; color:var(--text-muted);">TEMP</div>
          <div style="font-size:0.9rem; font-weight:600;">${b.temperature}°C</div>
        </div>
        <div>
          <div style="font-size:0.7rem; color:var(--text-muted);">GAS/ODOR</div>
          <div style="font-size:0.9rem; font-weight:600;">${b.gas_level} ppm</div>
        </div>
      </div>
    </div>
  `;
}

async function triggerSimulateTick() {
  try {
    const res = await API.simulateTick();
    showToast(`Simulation tick complete: ${res.updated_bins_count} bins updated.`, "success");
    loadIoTBins();
    if (window.refreshOverviewData) window.refreshOverviewData();
  } catch (err) {
    showToast(`Simulation error: ${err.message}`, "error");
  }
}

async function sendManualTelemetry() {
  const binId = document.getElementById("sim-bin-select").value;
  const fillPct = parseFloat(document.getElementById("sim-fill-slider").value);
  const weightKg = parseFloat(document.getElementById("sim-weight-slider").value);
  const tempC = parseFloat(document.getElementById("sim-temp-slider").value);
  const gasPpm = parseFloat(document.getElementById("sim-gas-slider").value);

  try {
    await API.simulateTick({
      bin_id: binId,
      fill_percentage: fillPct,
      weight_kg: weightKg,
      temperature: tempC,
      gas_level: gasPpm
    });
    showToast(`Manual telemetry transmitted to ${binId}!`, "success");
    loadIoTBins();
    if (window.refreshOverviewData) window.refreshOverviewData();
  } catch (err) {
    showToast(`Manual send failed: ${err.message}`, "error");
  }
}

function toggleAutoSimulation() {
  const btn = document.getElementById("auto-sim-btn");
  if (autoSimInterval) {
    clearInterval(autoSimInterval);
    autoSimInterval = null;
    btn.textContent = "Start Auto-Simulation";
    btn.classList.remove("btn-primary");
    btn.classList.add("btn-outline");
    showToast("Auto-simulation stopped.", "info");
  } else {
    autoSimInterval = setInterval(() => {
      API.simulateTick().then(() => {
        loadIoTBins();
        if (window.refreshOverviewData) window.refreshOverviewData();
      });
    }, 12000);
    btn.textContent = "Stop Auto-Simulation";
    btn.classList.remove("btn-outline");
    btn.classList.add("btn-primary");
    showToast("Auto-simulation active (12s interval).", "success");
  }
}
