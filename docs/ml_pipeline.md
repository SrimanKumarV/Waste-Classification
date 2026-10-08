# Machine Learning & Explainability Pipeline

## 1. Computer Vision Architecture

The classification subsystem identifies waste items across 12 distinct classes and maps them to appropriate segregation bins:

```
Input Image (RGB)
      │
      ▼
Image Preprocessing: Resize to (256, 256) & Normalization [0, 1]
      │
      ▼
Active Neural Backbone (VGG16 / Custom CNN / ResNet50 / MobileNetV3)
      │
      ▼
Softmax Activation Layer (12 Class Probabilities)
      │
      ▼
Confidence Threshold Evaluation (τ = 0.70)
      ├── If Confidence < 0.70 ──► UNCERTAIN Classification / Retake Request
      └── If Confidence ≥ 0.70 ──► Predicted Class & Recommended Dustbin
```

---

## 2. 12 Waste Classes & Dustbin Mapping

| Class Name | Broad Category | Target Dustbin | Disposal Guidance |
| :--- | :--- | :--- | :--- |
| **battery** | Hazardous | 🟥 Hazardous (Red Bin) | Prevent chemical leaching; deliver to e-waste station |
| **biological** | Organic | 🟩 Organic (Green Bin) | Biodegradable compost; wet kitchen waste |
| **brown-glass** | Recyclable | 🟦 Recyclable (Blue Bin) | Bottle recycling; rinse clean |
| **cardboard** | Recyclable | 🟦 Recyclable (Blue Bin) | Flatten boxes to save bin volume |
| **clothes** | Recyclable | 🟦 Recyclable (Blue Bin) | Textile sorting & fabric recovery |
| **green-glass** | Recyclable | 🟦 Recyclable (Blue Bin) | Glass cullet recycling |
| **metal** | Recyclable | 🟦 Recyclable (Blue Bin) | Tin cans, foil, scrap metal |
| **paper** | Recyclable | 🟦 Recyclable (Blue Bin) | Dry clean paper, notebooks |
| **plastic** | Recyclable | 🟦 Recyclable (Blue Bin) | PET bottles, containers |
| **shoes** | Recyclable | 🟦 Recyclable (Blue Bin) | Rubber and composite recovery |
| **trash** | Organic | 🟩 Organic (Green Bin) | Mixed non-recyclable solid organic waste |
| **white-glass** | Recyclable | 🟦 Recyclable (Blue Bin) | Clear glass jars and containers |

---

## 3. Model Registry & Empirical Benchmarks

The platform supports hot-swapping between models via the Model Registry. The metrics below are empirically measured from research notebooks in this repository:

| Model Architecture | Backbone Design | Test Accuracy | Precision | Recall | F1-Score | Inference Latency | Parameters | Edge Feasibility |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **VGG16 (Active)** | 13 Conv + 3 Dense | **89.13%** | 89.0% | 88.0% | **0.880** | 145 ms | 14.7M | Server / GPU |
| **Custom CNN** | 6 Conv2D + BatchNorm | **86.13%** | 85.2% | 84.1% | **0.846** | 92 ms | 8.4M | Moderate Edge |
| **ResNet-50** | Residual Blocks | **53.40%** | 52.1% | 50.5% | **0.512** | 119 ms | 23.5M | Heavy Backbone |
| **MobileNetV3** | Inverted Residuals | **57.76%** | 56.4% | 55.1% | **0.557** | **42 ms** | **2.9M** | **Ideal for ESP32/RPi** |
| **Ensemble** | Soft Probability Voting | **91.25%** | 90.8% | 90.1% | **0.904** | 235 ms | 46.6M | Multi-model Server |

---

## 4. Grad-CAM Interpretability

Grad-CAM (Gradient-weighted Class Activation Mapping) produces visual explanations by computing the gradient of the predicted class score $y^c$ with respect to feature activation map $A^k$ of the final convolutional layer:

$$\alpha_k^c = \frac{1}{Z} \sum_i \sum_j \frac{\partial y^c}{\partial A_{i,j}^k}$$

$$L_{\text{Grad-CAM}}^c = \text{ReLU}\left(\sum_k \alpha_k^c A^k\right)$$

The resulting heatmap is upsampled and blended over the input image. This ensures stakeholders can visually verify whether the model is focusing on the actual item (e.g. plastic bottle cap and texture) rather than background noise.
