from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import cv2
import numpy as np
import base64
import google.generativeai as genai
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app)

# Load your trained model
model = tf.keras.models.load_model('plant_classification_model.h5')

# Set up Gemini API
API_KEY = "GAIzaSyC0_TqjmObxyOmLUY35_opTSq0MFVbrVsY"  # Replace with your actual Gemini API key
genai.configure(api_key=API_KEY)

def preprocess_image(image):
    image = cv2.resize(image, (224, 224))
    image = image.astype(np.float32) / 255.0
    return np.expand_dims(image, axis=0)

def get_plant_fact(plant_name):
    try:
        model_gemini = genai.GenerativeModel('gemini-pro')
        prompt = f"Tell me an interesting fact about the {plant_name} plant. Keep it short and concise."
        response = model_gemini.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating fact: {str(e)}")
        return "Unable to generate fact due to an API error."

@app.route('/api/predict_and_fact', methods=['POST'])
def predict_and_fact():
    try:
        image_data = request.json['image']
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        # Decode the image
        try:
            image_data = base64.b64decode(image_data.split(',')[1])
            image = Image.open(BytesIO(image_data))
            image = image.convert('RGB')
            image = np.array(image)
        except Exception as e:
            return jsonify({'error': f'Image decoding failed: {str(e)}'}), 400

        preprocessed_image = preprocess_image(image)
        prediction = model.predict(preprocessed_image)[0][0]
        
        class_name = "YELLOW SNAKE" if prediction > 0.5 else "ARECA PALM"
        confidence = float(prediction) if prediction > 0.5 else float(1 - prediction)

        fact = get_plant_fact(class_name)

        return jsonify({
            'prediction': {
                'class': class_name,
                'confidence': confidence
            },
            'fact': fact
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)