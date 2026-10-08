from flask import Flask, request, render_template
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from io import BytesIO  # For file handling
import base64

app = Flask(__name__)
model = load_model("best_model_multi.h5")

# Define your 12 classes in the same order as training
class_names = [
    "battery", "biological", "brown-glass", "cardboard", "clothes",
    "green-glass", "metal", "paper", "plastic", "shoes", "trash", "white-glass"
]

# Mapping each class to a dustbin category
category_map = {
    "battery": "Hazardous (Red Bin)",
    "biological": "Organic (Green Bin)",
    "brown-glass": "Recyclable (Blue Bin)",
    "cardboard": "Recyclable (Blue Bin)",
    "clothes": "Recyclable (Blue Bin)",
    "green-glass": "Recyclable (Blue Bin)",
    "metal": "Recyclable (Blue Bin)",
    "paper": "Recyclable (Blue Bin)",
    "plastic": "Recyclable (Blue Bin)",
    "shoes": "Recyclable (Blue Bin)",
    "trash": "Organic (Green Bin)",
    "white-glass": "Recyclable (Blue Bin)"
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    file = request.files['file']

    # Check if file is uploaded
    if not file:
        return render_template("index.html", prediction="No file uploaded")

    # Read image and preprocess
    img = image.load_img(BytesIO(file.read()), target_size=(256, 256))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # add batch dimension
    img_array /= 255.0  # normalize

    # Prediction
    prediction = model.predict(img_array)  # shape (1,12)
    predicted_class_index = np.argmax(prediction, axis=1)[0]
    predicted_class = class_names[predicted_class_index]
    confidence = np.max(prediction) * 100  # highest probability %

    # Map to dustbin category
    dustbin_category = category_map[predicted_class]

    # Rewind file pointer to encode uploaded image
    file.stream.seek(0)
    img_bytes = file.read()
    encoded_img = base64.b64encode(img_bytes).decode('utf-8')
    uploaded_img = f"data:image/png;base64,{encoded_img}"

    return render_template(
        "index.html",
        prediction=predicted_class,
        confidence=f"{confidence:.2f}%",
        dustbin=dustbin_category,
        uploaded_img=uploaded_img
    )

if __name__ == "__main__":
    app.run(debug=True)
