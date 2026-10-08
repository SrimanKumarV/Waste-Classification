// Main Dashboard Controller & Visualization Engine

let trendChart = null;
let categoryChart = null;
let locationChart = null;

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  initScanner();
  loadAllDashboardData();

  // Periodic background refresh every 20 seconds
  setInterval(() => {
    refreshOverviewData();
    loadIoTBins();
  }, 20000);
});

// Tab Navigation
function initNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach(item => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const tabId = item.dataset.tab;
      switchTab(tabId);
    });
  });
}

function switchTab(tabId) {
  document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".tab-section").forEach(el => el.classList.remove("active"));

  const targetNav = document.querySelector(`.nav-item[data-tab="${tabId}"]`);
  const targetSection = document.getElementById(`tab-${tabId}`);

  if (targetNav) targetNav.classList.add("active");
  if (targetSection) targetSection.classList.add("active");

  const titleMap = {
    overview: "Operational Overview & KPIs",
    scanner: "AI Waste Classification & Auditing",
    analytics: "Segregation Analytics & Heatmaps",
    iot: "Real-Time IoT Bin Monitoring",
    predictions: "Predictive Analytics & Fill Forecasting",
    recommendations: "Decision Support & Recommendations",
    energy: "SDG 7 — Energy-Aware Collection Planning",
    evaluation: "Academic Model & System Evaluation",
    simulator: "IoT Sensor Gateway Simulator"
  };

  document.getElementById("page-title").textContent = titleMap[tabId] || "Dashboard";

  // Lazy tab data loading
  if (tabId === "iot") loadIoTBins();
  if (tabId === "predictions") loadPredictionsData();
  if (tabId === "recommendations") loadRecommendationsData();
  if (tabId === "energy") loadEnergyData();
  if (tabId === "evaluation") loadEvaluationData();
  if (tabId === "analytics") loadAnalyticsDeepDive();
}

// Load All Initial Data
async function loadAllDashboardData() {
  await refreshOverviewData();
  await loadIoTBins();
  await loadRecentAuditsTable();
}

async function refreshOverviewData() {
  try {
    const kpis = await API.getOverview();
    
    // KPI Cards
    document.getElementById("kpi-efficiency").textContent = `${kpis.segregation_efficiency_pct}%`;
    document.getElementById("kpi-audits").textContent = kpis.total_audits.toLocaleString();
    document.getElementById("kpi-contamination").textContent = `${kpis.contamination_rate_pct}%`;
    document.getElementById("kpi-critical-bins").textContent = kpis.critical_bins;
    document.getElementById("kpi-today").textContent = kpis.today_audits;
    document.getElementById("kpi-confidence").textContent = `${kpis.avg_confidence_pct}%`;
    document.getElementById("kpi-latency").textContent = `${kpis.avg_response_time_ms} ms`;

    // Charts
    renderOverviewCharts();
  } catch (err) {
    console.error("Error refreshing overview:", err);
  }
}

window.refreshOverviewData = refreshOverviewData;

// Charts
async function renderOverviewCharts() {
  try {
    const trends = await API.getTrends(14);
    const waste = await API.getWasteDistribution();

    // 1. Efficiency Trend Chart
    const trendCtx = document.getElementById("trend-chart")?.getContext("2d");
    if (trendCtx) {
      if (trendChart) trendChart.destroy();
      trendChart = new Chart(trendCtx, {
        type: "line",
        data: {
          labels: trends.map(t => t.display_date),
          datasets: [
            {
              label: "Segregation Efficiency (%)",
              data: trends.map(t => t.efficiency_pct),
              borderColor: "#10b981",
              backgroundColor: "rgba(16, 185, 129, 0.1)",
              fill: true,
              tension: 0.3,
              borderWidth: 2
            },
            {
              label: "Total Audited Items",
              data: trends.map(t => t.total),
              borderColor: "#3b82f6",
              borderDash: [5, 5],
              fill: false,
              tension: 0.3,
              yAxisID: "y1"
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { labels: { color: "#9ca3af" } } },
          scales: {
            x: { grid: { color: "#1f2937" }, ticks: { color: "#9ca3af" } },
            y: { grid: { color: "#1f2937" }, ticks: { color: "#9ca3af" }, min: 0, max: 100 },
            y1: { position: "right", grid: { display: false }, ticks: { color: "#9ca3af" } }
          }
        }
      });
    }

    // 2. Category Donut Chart
    const catCtx = document.getElementById("category-chart")?.getContext("2d");
    if (catCtx) {
      if (categoryChart) categoryChart.destroy();
      const labels = Object.keys(waste.categories);
      const values = Object.values(waste.categories);

      categoryChart = new Chart(catCtx, {
        type: "doughnut",
        data: {
          labels: labels,
          datasets: [{
            data: values,
            backgroundColor: ["#3b82f6", "#10b981", "#ef4444"],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: "bottom", labels: { color: "#9ca3af" } } }
        }
      });
    }
  } catch (err) {
    console.error("Error rendering charts:", err);
  }
}

// Analytics Deep Dive
async function loadAnalyticsDeepDive() {
  try {
    const locs = await API.getLocations();
    const heatmapBox = document.getElementById("location-heatmap-grid");
    if (heatmapBox) {
      heatmapBox.innerHTML = locs.map(l => `
        <div class="card" style="border-left: 5px solid ${l.heatmap_color};">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>${l.location_name}</strong>
            <span class="badge-status" style="background:${l.heatmap_color}22; color:${l.heatmap_color};">${l.performance_tier}</span>
          </div>
          <div style="font-size:2rem; font-weight:700; color:${l.heatmap_color}; margin:8px 0;">
            ${l.efficiency_pct}%
          </div>
          <div style="font-size:0.8rem; color:var(--text-secondary);">
            Audited: <strong>${l.total_audits}</strong> | Contamination: <strong>${l.contamination_pct}%</strong>
          </div>
        </div>
      `).join("");
    }

    // Top contaminants list
    const waste = await API.getWasteDistribution();
    const contamList = document.getElementById("top-contaminants-list");
    if (contamList) {
      contamList.innerHTML = waste.top_contaminants.map((c, i) => `
        <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid var(--border-subtle);">
          <span>#${i+1} <strong>${c.item.toUpperCase()}</strong></span>
          <span style="color:#ef4444; font-weight:600;">${c.count} misplaced incidents</span>
        </div>
      `).join("");
    }
  } catch (err) {
    console.error("Error loading analytics:", err);
  }
}

// Predictions Tab
async function loadPredictionsData() {
  try {
    const preds = await API.getAllPredictions();
    const trendPred = await API.getTrendPrediction();

    // Trend banner
    const trendBox = document.getElementById("trend-prediction-banner");
    if (trendBox) {
      const isImp = trendPred.trend === "Improving";
      trendBox.innerHTML = `
        <div class="card" style="border-left: 5px solid ${isImp ? '#10b981' : '#f59e0b'};">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <strong>Segregation Efficiency 7-Day Moving Trend</strong>
              <div style="font-size:0.85rem; color:var(--text-secondary); margin-top:2px;">
                Current: ${trendPred.current_efficiency_pct}% | Prior Week: ${trendPred.prior_week_efficiency_pct}%
              </div>
            </div>
            <div style="text-align:right;">
              <span class="badge-status ${isImp ? 'status-NORMAL' : 'status-HIGH'}" style="font-size:0.9rem;">
                ${trendPred.trend.toUpperCase()} (${trendPred.delta_pct > 0 ? '+' : ''}${trendPred.delta_pct}%)
              </span>
              <div style="font-size:0.8rem; color:var(--text-muted); margin-top:4px;">
                Forecast Next Week: <strong>${trendPred.predicted_next_week_pct}%</strong>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    // Predictions Table
    const tbody = document.getElementById("predictions-table-body");
    if (tbody) {
      tbody.innerHTML = preds.map(p => `
        <tr>
          <td><strong>${p.bin_id}</strong></td>
          <td>${p.current_fill_percentage}%</td>
          <td><span style="color:${p.predicted_fill_4h >= 80 ? '#ef4444' : '#fff'}; font-weight:600;">${p.predicted_fill_4h}%</span></td>
          <td><span style="color:${p.predicted_fill_8h >= 80 ? '#ef4444' : '#fff'}; font-weight:600;">${p.predicted_fill_8h}%</span></td>
          <td>${p.predicted_fill_24h}%</td>
          <td><strong>${p.expected_critical_time || 'N/A'}</strong></td>
          <td><span class="badge-status status-NORMAL">MAE: ${p.model_evaluation.mae}%</span></td>
        </tr>
      `).join("");
    }
  } catch (err) {
    console.error("Error loading predictions:", err);
  }
}

// Recommendations Tab
async function loadRecommendationsData() {
  try {
    const recs = await API.getRecommendations();
    const container = document.getElementById("recommendations-list");
    if (container) {
      container.innerHTML = recs.map(r => `
        <div class="rec-card ${r.priority}">
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
              <span class="badge-status status-${r.priority === 'CRITICAL' ? 'CRITICAL' : (r.priority === 'HIGH' ? 'HIGH' : 'NORMAL')}">${r.priority} PRIORITY</span>
              <span style="font-size:0.8rem; color:var(--text-muted); margin-left:8px;">${r.location_name}</span>
              <h4 class="rec-title" style="margin-top:6px;">${r.title}</h4>
            </div>
            <div>
              <button class="btn btn-outline" style="font-size:0.75rem; padding:4px 10px;" onclick="updateRecStatus(${r.id}, '${r.status === 'ACTIVE' ? 'RESOLVED' : 'ACTIVE'}')">
                ${r.status === 'ACTIVE' ? 'Mark Resolved' : 'Reopen'}
              </button>
            </div>
          </div>
          <div class="rec-reason"><strong>Data Reason:</strong> ${r.reason}</div>
          <div class="rec-action"><strong>Recommended Action:</strong> ${r.recommendation}</div>
          ${r.expected_benefit ? `<div style="font-size:0.78rem; color:var(--text-muted); margin-top:6px;"><strong>Expected Benefit:</strong> ${r.expected_benefit}</div>` : ''}
        </div>
      `).join("");
    }
  } catch (err) {
    console.error("Error loading recommendations:", err);
  }
}

async function updateRecStatus(recId, newStatus) {
  try {
    await API.updateRecommendationStatus(recId, newStatus);
    showToast(`Recommendation updated to ${newStatus}`, "success");
    loadRecommendationsData();
  } catch (err) {
    showToast(`Update error: ${err.message}`, "error");
  }
}

// SDG 7 Clean Energy Tab
async function loadEnergyData() {
  try {
    const plan = await API.getEnergyPlan();

    document.getElementById("energy-trips-avoided").textContent = plan.trips_avoided_week;
    document.getElementById("energy-fuel-saved").textContent = `${plan.fuel_saved_liters} L`;
    document.getElementById("energy-kwh-saved").textContent = `${plan.energy_saved_kwh} kWh`;
    document.getElementById("energy-co2-reduced").textContent = `${plan.co2_reduction_kg} kg`;
    document.getElementById("energy-percent-reduction").textContent = `${plan.percent_reduction}%`;

    const routeTable = document.getElementById("route-sequence-table-body");
    if (routeTable) {
      routeTable.innerHTML = plan.priority_collection_route.map(r => `
        <tr>
          <td><strong>#${r.sequence_order}</strong></td>
          <td><strong>${r.bin_id}</strong></td>
          <td>${r.location_name}</td>
          <td>${r.bin_type}</td>
          <td><strong>${r.fill_percentage}%</strong></td>
          <td>${r.weight_kg} kg</td>
          <td>
            <span class="badge-status ${r.dispatch_action === 'IMMEDIATE' ? 'status-CRITICAL' : (r.dispatch_action === 'SCHEDULED' ? 'status-HIGH' : 'status-NORMAL')}">
              ${r.dispatch_action}
            </span>
          </td>
        </tr>
      `).join("");
    }
  } catch (err) {
    console.error("Error loading energy plan:", err);
  }
}

// Academic Model Evaluation Tab
async function loadEvaluationData() {
  try {
    const modelsData = await API.getModels();
    const tbody = document.getElementById("model-comparison-table-body");
    if (tbody) {
      tbody.innerHTML = modelsData.models.map(m => `
        <tr style="${m.is_active ? 'background:rgba(16, 185, 129, 0.08);' : ''}">
          <td>
            <strong>${m.name}</strong>
            ${m.is_active ? ' <span class="badge-status status-NORMAL">ACTIVE</span>' : ''}
          </td>
          <td>${m.architecture}</td>
          <td><strong>${(m.accuracy * 100).toFixed(2)}%</strong></td>
          <td>${(m.precision * 100).toFixed(1)}%</td>
          <td>${(m.recall * 100).toFixed(1)}%</td>
          <td><strong>${(m.f1_score * 100).toFixed(1)}%</strong></td>
          <td>${m.avg_inference_ms} ms</td>
          <td>${m.parameters}</td>
          <td>
            ${!m.is_active ? `
              <button class="btn btn-outline" style="font-size:0.75rem; padding:4px 8px;" onclick="switchActiveModel('${m.key}')">
                Activate
              </button>
            ` : '<span>Active</span>'}
          </td>
        </tr>
      `).join("");
    }
  } catch (err) {
    console.error("Error loading model metrics:", err);
  }
}

async function switchActiveModel(modelKey) {
  try {
    await API.setActiveModel(modelKey);
    showToast(`Activated ${modelKey} as active inference model.`, "success");
    loadEvaluationData();
  } catch (err) {
    showToast(`Error activating model: ${err.message}`, "error");
  }
}

// Recent Audits Table
async function loadRecentAuditsTable() {
  try {
    const data = await API.getAudits(15, 0);
    const tbody = document.getElementById("recent-audits-table-body");
    if (tbody) {
      tbody.innerHTML = data.audits.map(a => `
        <tr>
          <td>#${a.id}</td>
          <td><strong>${a.waste_class.toUpperCase()}</strong></td>
          <td>${a.location_name}</td>
          <td>${a.expected_bin}</td>
          <td>${a.actual_bin}</td>
          <td>
            <span class="badge-status status-${a.segregation_status}">
              ${a.segregation_status}
            </span>
          </td>
          <td>${(a.confidence * 100).toFixed(1)}%</td>
          <td>${a.response_time_ms} ms</td>
        </tr>
      `).join("");
    }
  } catch (err) {
    console.error("Error loading recent audits:", err);
  }
}

// Utility Toast
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `
    <span>${type === 'success' ? '✅' : (type === 'error' ? '❌' : 'ℹ️')}</span>
    <span>${message}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 4000);
}
