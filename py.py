from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import cv2
import numpy as np
import base64
import requests  # To call the Gemini API
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app)

# Load your trained model
model = tf.keras.models.load_model('classification_model76.h5')

# Define the class labels for your 8 classes
class_names = [
    "ALOE VERA",
    "ANTHURIUM",
    "ARECA PALM",
    "HOLY BASIL",
    "MIMOSA PUDICA",
    "MONEY PLANT",
    "SPIDER PLANT",
    "YELLOW SNAKE"
]

# Gemini API Key
GEMINI_API_KEY = "AIzaSyBPJoPtPj-sZTTAkmOOzdeYtuxqib3UvNg"  # Replace with your actual Gemini API key

def preprocess_image(image):
    """Preprocess the image for prediction"""
    image = cv2.resize(image, (150, 150))  # Resize to the size your model expects (150x150 here)
    image = image.astype(np.float32) / 255.0  # Normalize pixel values
    return np.expand_dims(image, axis=0)  # Add batch dimension

def get_fun_fact_and_tips(plant_name):
    """Fetch a fun fact and growing tips about the plant"""
    try:
        headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
        response = requests.get(f"https://gemini-api.com/plants/{plant_name}", headers=headers)
        data = response.json()

        # Extract the fun fact and growing tips
        fun_fact = data.get('fun_fact', 'No fun fact available.')
        growing_tips = data.get('growing_tips', 'No growing tips available.')

        return fun_fact, growing_tips
    except Exception as e:
        print(f"API error: {str(e)}")
        return "Fun fact not available.", "Growing tips not available."

@app.route('/api/predict', methods=['POST'])
def predict():
    """API endpoint to predict plant class and fetch information"""
    try:
        image_data = request.json['image']
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        # Decode the image from base64
        try:
            image_data = base64.b64decode(image_data.split(',')[1])
            image = Image.open(BytesIO(image_data))
            image = image.convert('RGB')  # Convert to RGB
            image = np.array(image)
        except Exception as e:
            return jsonify({'error': f'Image decoding failed: {str(e)}'}), 400

        # Preprocess the image
        preprocessed_image = preprocess_image(image)

        # Predict using the model
        predictions = model.predict(preprocessed_image)[0]
        
        # Get the predicted class and its confidence
        predicted_class_idx = np.argmax(predictions)
        class_name = class_names[predicted_class_idx]
        confidence = float(predictions[predicted_class_idx])

        # Fetch a fun fact and growing tips
        fun_fact, growing_tips = get_fun_fact_and_tips(class_name)

        return jsonify({
            'prediction': {
                'class': class_name,
                'confidence': confidence
            },
            'info': {
                'fun_fact': fun_fact,
                'growing_tips': growing_tips
            }
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
