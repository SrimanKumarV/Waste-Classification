# REST API Reference Manual

Interactive OpenAPI (Swagger) UI is available at `http://127.0.0.1:8000/docs`.

---

## 1. Machine Learning & Inference

### `POST /api/waste/predict`
Uploads waste image for classification and bin mapping.
- **Form Data**: `file` (Image binary)
- **Query Params**: `confidence_threshold` (default: 0.70), `generate_explainability` (default: true)
- **Response**:
```json
{
  "success": true,
  "waste_class": "plastic",
  "waste_category": "Recyclable",
  "recommended_bin": "Recyclable (Blue Bin)",
  "confidence": 0.946,
  "is_confident": true,
  "confidence_threshold": 0.7,
  "model_name": "VGG16 (Transfer Learning)",
  "inference_time_ms": 142.5,
  "all_probabilities": { "plastic": 0.946, "paper": 0.021, ... },
  "explainability_url": "data:image/png;base64,..."
}
```

### `GET /api/models`
Returns model registry and empirical metrics table.

### `POST /api/models/active`
Switches active inference model.

---

## 2. Waste Auditing & Feedback

### `POST /api/audits`
Records waste audit event and evaluates segregation status.
- **Payload**:
```json
{
  "waste_class": "plastic",
  "actual_bin": "Organic (Green Bin)",
  "confidence": 0.94,
  "location_id": 5,
  "bin_id": "BIN-003"
}
```
- **Response**:
```json
{
  "id": 532,
  "waste_class": "plastic",
  "expected_bin": "Recyclable (Blue Bin)",
  "actual_bin": "Organic (Green Bin)",
  "segregation_status": "INCORRECT",
  "created_at": "2026-10-08T14:20:01"
}
```

### `POST /api/feedback`
Records stakeholder usefulness rating (1-5 stars) and comments.

---

## 3. Analytics & Heatmaps

- `GET /api/analytics/overview?days=30`: Segregation efficiency %, contamination rate %, total audits, critical bins.
- `GET /api/analytics/locations?days=30`: Campus location segregation rankings and color-graded heatmap data.
- `GET /api/analytics/waste?days=30`: 12-class breakdown and top contaminants.
- `GET /api/analytics/trends?days=14`: Daily efficiency and volume trends.

---

## 4. IoT & Telemetry

- `GET /api/iot/bins`: Live sensor readings for all campus bins.
- `POST /api/iot/sensor`: Hardware telemetry ingestion from ESP32.
- `POST /api/iot/simulate`: Triggers time-step simulation or manual slider override.

---

## 5. Predictive Analytics & Decision Support

- `GET /api/predictions/bins/{bin_id}`: Fill level forecast at +4h, +8h, +24h and hours to critical.
- `GET /api/predictions/trend`: 7-day moving trend forecast (Improving / Declining).
- `GET /api/recommendations`: Actionable recommendations with data-backed rationales.
- `GET /api/energy/collection-plan`: SDG 7 energy-aware route sequence, trips avoided, liters diesel saved.
