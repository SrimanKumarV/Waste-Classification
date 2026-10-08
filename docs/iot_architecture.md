# IoT Architecture & Telemetry Specification

## 1. Physical Hardware & Sensor Gateway Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Smart Bin Sensor Node                     │
│                                                             │
│  [Ultrasonic HC-SR04] ────► Bin Fill Percentage (0-100%)    │
│  [Load Cell HX711]    ────► Waste Accumulation Weight (kg)  │
│  [DHT22 / DS18B20]    ────► Interior Temperature (°C)       │
│  [MQ-135 Gas Sensor]  ────► Decomposition Odor Index (ppm)  │
│                                                             │
│                         ▼                                   │
│            ESP32 Microcontroller Gateway                    │
│             (Wi-Fi / 4G LTE / MQTT / HTTP)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ POST /api/iot/sensor (JSON)
                          ▼
            FastAPI Cloud Telemetry Ingestion Layer
                          │
                          ▼
          PostgreSQL / SQLite Database & Analytics Store
```

---

## 2. Sensor Payload Schema

```json
{
  "device_id": "ESP32-GATEWAY-001",
  "bin_id": "BIN-003",
  "fill_percentage": 82.4,
  "weight_kg": 18.5,
  "temperature": 31.2,
  "gas_level": 145.0,
  "timestamp": "2026-10-08T18:30:00Z"
}
```

---

## 3. Bin Operational Capacity Levels

| Fill Range | Status | Operational Action |
| :--- | :--- | :--- |
| **0% – 50%** | `NORMAL` | Normal waste generation; no collection required |
| **51% – 75%** | `MODERATE` | Regular tracking; stable state |
| **76% – 90%** | `HIGH` | Added to next scheduled collection dispatch |
| **91% – 100%** | `CRITICAL` | **Urgent Dispatch Triggered**: Emits critical notification and generates high-priority janitorial recommendation |

---

## 4. Realistic Diurnal Accumulation Simulator

When physical hardware nodes are in transit or undergoing maintenance, the built-in **Simulation Engine** accurately models diurnal campus waste patterns:
- **Lunch Peak (12:00 PM – 2:30 PM)**: Accumulation rate increases by $2.5\times$ (driven by cafeteria food court and food containers).
- **Evening Rush (5:00 PM – 8:00 PM)**: Accumulation rate increases by $2.0\times$.
- **Night Hours (10:00 PM – 6:00 AM)**: Flat accumulation ($\approx 0.2\times$).
- **Weight Correlation**: Strongly models load cell readings ($0.18\text{ to }0.24\text{ kg per 1\% fill}$).
- **Gas / Odor Emission**: Organic bins exhibit non-linear VOC and gas emission spikes as fill levels exceed $80\%$, signaling decomposition.
