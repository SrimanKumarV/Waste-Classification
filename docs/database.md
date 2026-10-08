# Database Architecture & Schema Specification

## 1. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ WASTE_AUDITS : logs
    LOCATIONS ||--o{ BINS : contains
    LOCATIONS ||--o{ WASTE_AUDITS : locates
    LOCATIONS ||--o{ RECOMMENDATIONS : targets
    BINS ||--o{ SENSOR_READINGS : emits
    BINS ||--o{ WASTE_AUDITS : receives
    BINS ||--o{ PREDICTIONS : forecasts
    WASTE_AUDITS ||--o| USER_FEEDBACK : evaluates

    USERS {
        int id PK
        string name
        string email
        string password_hash
        string role
        datetime created_at
    }

    LOCATIONS {
        int id PK
        string name
        string description
        float latitude
        float longitude
    }

    BINS {
        string id PK
        int location_id FK
        string bin_type
        float capacity_kg
        string status
        float fill_percentage
        float weight_kg
        float temperature
        float gas_level
        datetime last_updated
    }

    WASTE_AUDITS {
        int id PK
        int user_id FK
        int location_id FK
        string bin_id FK
        string image_url
        string waste_class
        string waste_category
        float confidence
        string expected_bin
        string actual_bin
        string segregation_status
        string model_name
        string model_version
        float response_time_ms
        datetime created_at
    }

    SENSOR_READINGS {
        int id PK
        string bin_id FK
        float fill_percentage
        float weight_kg
        float temperature
        float gas_level
        datetime timestamp
    }

    PREDICTIONS {
        int id PK
        string bin_id FK
        string prediction_type
        float predicted_value
        datetime target_time
        float confidence
        datetime created_at
    }

    RECOMMENDATIONS {
        int id PK
        int location_id FK
        string priority
        string title
        text reason
        text recommendation
        string expected_benefit
        string status
        datetime created_at
    }

    MODEL_METRICS {
        int id PK
        string model_name
        string model_version
        float accuracy
        float precision
        float recall
        float f1_score
        float mae
        float rmse
        float average_response_time_ms
        string parameters
        boolean is_active
        datetime created_at
    }

    USER_FEEDBACK {
        int id PK
        int audit_id FK
        int rating
        string feedback_type
        text comments
        datetime created_at
    }
```

---

## 2. Table Specifications & Integrity Constraints

### `waste_audits`
- **Purpose**: Primary audit ledger tracking every verified waste disposal.
- **`segregation_status`**: Enforces tripartite categorization:
  - `CORRECT`: User placed item into the correct dustbin.
  - `INCORRECT`: Contamination occurred (e.g. plastic deposited in green bin).
  - `UNCERTAIN`: Image model confidence fell below threshold ($< 0.70$).
- **Indexes**: Indexed on `created_at` (for rolling window queries) and `location_id` (for campus heatmaps).

### `sensor_readings`
- **Purpose**: High-frequency telemetry log from ultrasonic fill sensors, load cells, temperature probes, and gas sensors.
- **Indexes**: Indexed on `bin_id` and `timestamp`.

### `model_metrics`
- **Purpose**: Academic audit log storing measured test accuracy, F1, latency, and parameter count for every registered deep learning architecture.
