# System Architecture — Smart Waste Segregation Analytics

## 1. High-Level System Architecture

The Smart Waste Segregation Analytics System transforms point-in-time waste classification into an end-to-end audit, IoT telemetry, and decision-support platform.

```mermaid
graph TD
    subgraph Clients["Presentation Layer"]
        A1[Web Analytics Dashboard]
        A2[Mobile PWA Auditor Client]
        A3[Flutter Cross-Platform App]
        A4[ESP32 / IoT Hardware Simulator]
    end

    subgraph Gateway["Backend Application Layer (FastAPI)"]
        B1[Auth & RBAC Middleware]
        B2[REST API Endpoints]
        B3[Background Task Workers]
    end

    subgraph Engines["Core Analytical & ML Engines"]
        C1[AI/ML Inference Engine<br/>12 Waste Classes + Grad-CAM]
        C2[Model Registry<br/>VGG16 / CNN / ResNet / MobileNet]
        C3[Waste Audit Engine<br/>Expected vs Actual Bin]
        C4[IoT Telemetry Engine<br/>Diurnal Simulator & Thresholds]
        C5[Predictive Analytics Engine<br/>Random Forest Fill Regressor]
        C6[Decision-Support Engine<br/>Rule & ML Assisted Recommendations]
        C7[SDG 7 Clean Energy Engine<br/>Dynamic Route Optimization]
    end

    subgraph Storage["Data & Model Store"]
        D1[(PostgreSQL / SQLite Database)]
        D2[HDF5 / Keras Model Store]
        D3[Historical Audit & Sensor Ledger]
    end

    Clients --> Gateway
    Gateway --> Engines
    Engines --> Storage
```

---

## 2. Multi-Module Processing Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor User as Auditor / Student
    participant UI as Web / Mobile UI
    participant API as FastAPI Backend
    participant ML as ML Inference Engine
    participant Audit as Waste Audit Engine
    participant DB as Relational Database
    participant Rec as Recommendation Engine

    User->>UI: Captures/Uploads waste image
    UI->>API: POST /api/waste/predict
    API->>ML: Preprocess (256x256) & Run Model
    ML-->>API: Waste Class (e.g. Plastic), Confidence (94.6%), Grad-CAM Overlay
    API-->>UI: Return Recommendation: Recyclable (Blue Bin)
    User->>UI: Selects Actual Bin used (e.g. Green Bin)
    UI->>API: POST /api/audits (waste_class, expected_bin, actual_bin)
    API->>Audit: Evaluate Expected vs Actual Bin
    Audit->>DB: Persist Audit record with status = INCORRECT
    Audit->>Rec: Trigger Contamination Check
    Rec->>DB: Generate "Plastic Contamination at Canteen" Recommendation
    API-->>UI: Return Audit Confirmation & Update KPIs
```

---

## 3. Data Flow Diagrams (DFD)

### Level 0 DFD (Context Diagram)
```mermaid
graph LR
    User([Auditor / Campus User]) -->|Uploads Image & Actual Bin| System((Smart Waste<br/>Segregation System))
    IoT([ESP32 / Sensors]) -->|Fill, Weight, Temp, Gas| System
    System -->|Classification & Bin Guidance| User
    System -->|Real-time KPIs & Heatmaps| Admin([Facility Manager])
    System -->|Dispatch Routes & Energy Savings| Logistics([Janitorial Staff])
```

### Level 1 DFD (Subsystem Interaction)
1. **P1.0 Image Ingestion & Preprocessing**: Validates format, resizes to $256 \times 256$, normalizes pixel values to $[0, 1]$.
2. **P2.0 Neural Inference & Saliency**: Generates class probabilities, applies confidence threshold ($0.70$), produces Grad-CAM heatmap.
3. **P3.0 Waste Auditing**: Maps predicted class to expected dustbin; verifies against physical bin used; labels status `CORRECT`, `INCORRECT`, or `UNCERTAIN`.
4. **P4.0 IoT Telemetry Processing**: Records fill %, load cell weight (kg), temperature (°C), gas (ppm); classifies status `NORMAL`, `MODERATE`, `HIGH`, `CRITICAL`.
5. **P5.0 Predictive Forecasting**: Runs Random Forest regression on temporal lag features to predict $+4h$, $+8h$, and $+24h$ fill levels.
6. **P6.0 Decision Support & SDG 7 Optimization**: Generates prioritized recommendations and computes vehicle fuel savings from demand-based routing.

---

## 4. SDG 7 — Affordable and Clean Energy Alignment

Traditional municipal waste collection runs on fixed daily schedules where trucks visit every bin regardless of fill level.
The system implements **Energy-Aware Collection Planning**:
- **Condition-Based Servicing**: Trucks are dispatched only to bins that are `HIGH` ($>75\%$) or predicted to hit `CRITICAL` ($>90\%$) before the next cycle.
- **Trip Reduction Modeling**:
  $$\text{Modeled Fuel Saved (L)} = \text{Trips Avoided} \times \text{Avg Trip Distance (km)} \times 0.28\text{ L/km}$$
  $$\text{Energy Equivalent (kWh)} = \text{Fuel Saved (L)} \times 10\text{ kWh/L}$$
  $$\text{Modeled }\text{CO}_2\text{ Reduction (kg)} = \text{Fuel Saved (L)} \times 2.68\text{ kg CO}_2\text{/L}$$
