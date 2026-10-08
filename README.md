# ♻️ Waste Classification & Segregation System

An intelligent waste classification and segregation system powered by Deep Learning, Computer Vision, and Natural Language Processing. The project classifies waste items into categories and maps them to appropriate disposal bins (Hazardous, Organic, Recyclable) to promote effective recycling and waste management.

---

## 📌 Project Features

- **Multi-Class Image Classification**: Classifies waste into 12 categories:
  - `battery`, `biological`, `brown-glass`, `cardboard`, `clothes`, `green-glass`, `metal`, `paper`, `plastic`, `shoes`, `trash`, `white-glass`
- **Smart Bin Mapping**:
  - **Hazardous (Red Bin)**: Batteries, toxic waste
  - **Organic (Green Bin)**: Biological waste, trash/food waste
  - **Recyclable (Blue Bin)**: Glass, paper, cardboard, plastics, metals, textiles, shoes
- **Multiple Deep Learning Architectures**:
  - Custom CNN
  - Transfer Learning: ResNet50, MobileNetV3, VGG16, VGG19
  - Ensemble Learning models
- **Speech & Text Classification**:
  - Speech-to-text recognition
  - Tamil dialect and multi-dialect text classification models
- **Interactive Web Interface**:
  - Flask-based web application with real-time image upload, prediction, confidence score, and bin recommendation.

---

## 📂 Repository Structure

```
├── Webpage/
│   ├── app.py                # Flask web application
│   └── templates/
│       └── index.html        # Interactive UI template
├── Custom CNN.ipynb          # Custom Convolutional Neural Network training
├── ResNet50.ipynb            # ResNet50 transfer learning notebook
├── MobileV3Net.ipynb         # MobileNetV3 model notebook
├── VGG16.ipynb               # VGG16 model notebook
├── VGG19.ipynb               # VGG19 model notebook
├── Ensemble Learning.ipynb   # Ensemble methods notebook
├── Speech_To_Text.ipynb      # Audio processing & speech recognition
├── Speech_To_Text(2).ipynb   # Extended speech recognition
├── Text_Classification.ipynb # Text-based waste classification
├── tamil_dialect_text_model.pkl # Trained Tamil dialect model
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore configuration
└── README.md                 # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.8+ installed.

### 2. Clone the Repository
```bash
git clone https://github.com/SrimanKumarV/Waste-Classification.git
cd Waste-Classification
```

### 3. Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🌐 Running the Web Application

1. Place your trained model weights (`best_model_multi.h5` or `best_model.h5`) in the `Webpage/` directory.
2. Navigate to the `Webpage/` folder:
   ```bash
   cd Webpage
   ```
3. Run the Flask application:
   ```bash
   python app.py
   ```
4. Open your browser and go to `http://127.0.0.1:5000/`. Upload an image to test classification and dustbin recommendation.

---

## 🧠 Model Training

Explore and run any of the Jupyter Notebooks:
- Open Jupyter Notebook:
  ```bash
  jupyter notebook
  ```
- Train or fine-tune models using `ResNet50.ipynb`, `Custom CNN.ipynb`, `MobileV3Net.ipynb`, etc.

---

## 📝 Note on Large Files & Datasets

Trained model weights (`*.h5`) and full raw datasets (`*.zip`, image directories) exceed GitHub's 100MB file limit and are excluded from version control via `.gitignore`. You can generate or download the weights by running the provided training notebooks.

---

## 👤 Author

- **Sriman Kumar V** - [GitHub Profile](https://github.com/SrimanKumarV)
