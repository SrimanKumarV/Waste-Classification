// Smart Waste Segregation Analytics — API Client

const API = {
  baseUrl: window.location.origin,

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP Error ${response.status}`);
      }
      return await response.json();
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },

  // Overview & Analytics
  getOverview(days = 30) {
    return this.request(`/api/analytics/overview?days=${days}`);
  },
  getLocations(days = 30) {
    return this.request(`/api/analytics/locations?days=${days}`);
  },
  getWasteDistribution(days = 30) {
    return this.request(`/api/analytics/waste?days=${days}`);
  },
  getTrends(days = 14) {
    return this.request(`/api/analytics/trends?days=${days}`);
  },

  // Machine Learning & Scanner
  predictWaste(file, threshold = 0.70, explain = true) {
    const formData = new FormData();
    formData.append("file", file);
    return this.request(`/api/waste/predict?confidence_threshold=${threshold}&generate_explainability=${explain}`, {
      method: "POST",
      body: formData
    });
  },
  getModels() {
    return this.request("/api/models");
  },
  setActiveModel(modelKey) {
    return this.request("/api/models/active", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_key: modelKey })
    });
  },

  // Audits & Feedback
  recordAudit(auditData) {
    return this.request("/api/audits", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(auditData)
    });
  },
  getAudits(limit = 50, offset = 0, locId = null, status = null) {
    let q = `/api/audits?limit=${limit}&offset=${offset}`;
    if (locId) q += `&location_id=${locId}`;
    if (status) q += `&segregation_status=${status}`;
    return this.request(q);
  },
  submitFeedback(data) {
    return this.request("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
  },
  getFeedbackStats() {
    return this.request("/api/feedback/stats");
  },

  // IoT & Bins
  getBins() {
    return this.request("/api/iot/bins");
  },
  getBinDetail(binId) {
    return this.request(`/api/iot/bins/${binId}`);
  },
  simulateTick(manualData = null) {
    return this.request("/api/iot/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: manualData ? JSON.stringify(manualData) : JSON.stringify({})
    });
  },
  sendSensorReading(reading) {
    return this.request("/api/iot/sensor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(reading)
    });
  },

  // Predictions
  getBinPrediction(binId) {
    return this.request(`/api/predictions/bins/${binId}`);
  },
  getAllPredictions() {
    return this.request("/api/predictions/all");
  },
  getTrendPrediction() {
    return this.request("/api/predictions/trend");
  },

  // Recommendations
  getRecommendations() {
    return this.request("/api/recommendations");
  },
  generateRecommendations() {
    return this.request("/api/recommendations/generate", { method: "POST" });
  },
  updateRecommendationStatus(id, newStatus) {
    return this.request(`/api/recommendations/${id}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
  },

  // SDG 7 Clean Energy
  getEnergyPlan() {
    return this.request("/api/energy/collection-plan");
  },

  // Campus Locations
  getCampusLocations() {
    return this.request("/api/locations");
  }
};
