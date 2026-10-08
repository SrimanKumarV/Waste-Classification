# User & Auditor Guide

## 1. Quick Start

### Starting the Server
```bash
py -3.12 run.py
```
- **Web Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Mobile Auditor View**: [http://127.0.0.1:8000/mobile](http://127.0.0.1:8000/mobile)
- **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 2. Auditor Workflow

```
1. Open http://127.0.0.1:8000 on your laptop or http://127.0.0.1:8000/mobile on phone.
2. Navigate to "Scan & Audit Waste".
3. Upload or capture an image of the discarded waste item.
4. Review the AI prediction:
   - Waste Type (e.g. PLASTIC)
   - Confidence Score (e.g. 94.6%)
   - Recommended Dustbin (e.g. Recyclable - Blue Bin)
   - Grad-CAM heatmap visualization
5. Confirm the actual bin the user discarded the item into:
   - Blue Bin (Recyclable)
   - Green Bin (Organic)
   - Red Bin (Hazardous)
6. Click "Confirm & Record Audit".
7. System immediately checks Expected vs Actual:
   - Displays ✅ CORRECT or ❌ INCORRECT (Contamination).
   - Automatically updates campus segregation efficiency and contamination metrics.
```

---

## 3. Facility Manager & IoT Monitoring Workflow

```
1. Navigate to "IoT Bin Monitoring" tab.
2. Review real-time fill levels, load weights, temperatures, and odor/gas readings.
3. Check status badges (NORMAL, MODERATE, HIGH, CRITICAL).
4. Inspect "Predictive Analytics" to see forecasted fill levels for +4h, +8h, and +24h.
5. Review "Decision Support & Recommendations":
   - Read transparent data-driven reasons for each alert.
   - Dispatch collection staff to critical bins before overflow occurs.
   - Click "Mark Resolved" when janitorial crew completes emptying.
6. Open "SDG 7 Clean Energy" to view optimized collection route sequence.
7. Download full audit ledger via "Export CSV".
```

---

## 4. Hardware Simulation Mode

```
1. Navigate to "IoT Simulator" tab.
2. Select any target smart bin (e.g. BIN-001).
3. Adjust sliders for Fill %, Weight, Temperature, and Gas level.
4. Click "Push Simulated Telemetry".
5. Live dashboard immediately updates to reflect the new sensor values.
6. Alternatively, click "Start Auto-Simulation" in the IoT tab to run automated diurnal accumulation loops.
```
