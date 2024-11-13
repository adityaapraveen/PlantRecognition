import React, { useRef, useState } from 'react';
import Webcam from 'react-webcam';
import './PlantRecognition.css';

const PlantRecognitionApp = () => {
  const webcamRef = useRef(null);
  const [imgSrc, setImgSrc] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [fact, setFact] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const capture = React.useCallback(async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImgSrc(imageSrc);
    await getPredictionAndFact(imageSrc);
  }, [webcamRef]);

  const resizeImage = (imageSrc) => {
    return new Promise((resolve) => {
      const img = new Image();
      img.src = imageSrc;
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = 224; // Desired width
        canvas.height = 224; // Desired height
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL('image/jpeg')); // Return the resized image
      };
    });
  };

  const getPredictionAndFact = async (imageSrc) => {
    setIsLoading(true);
    try {
      const resizedImageSrc = await resizeImage(imageSrc);
      console.log("Resized image source being sent: ", resizedImageSrc); // Log the resized imageSrc
      const response = await fetch('http://localhost:5000/api/predict_and_fact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: resizedImageSrc }),
      });

      // Check if the response is ok (status in the range 200-299)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPrediction(data.prediction);
      setFact(data.fact);
    } catch (error) {
      console.error('Error:', error);
      setPrediction({ error: 'Failed to get prediction and fact' });
    }
    setIsLoading(false);
  };

  return (
    <div className="container">
      <h1>Plant Recognition App</h1>
      <div className="webcam-container">
        <Webcam
          audio={false}
          ref={webcamRef}
          screenshotFormat="image/jpeg"
          videoConstraints={{ facingMode: 'environment' }}
          className="webcam"
        />
      </div>
      <div className="button-container">
        <button onClick={capture} className="capture-button">
          Capture and Recognize
        </button>
      </div>
      {isLoading && <p className="loading">Processing image...</p>}
      {prediction && !isLoading && (
        <div className="prediction">
          <h2>Prediction:</h2>
          <p>Plant: {prediction.class}</p>
          <p>Confidence: {(prediction.confidence * 100).toFixed(2)}%</p>
        </div>
      )}
      {fact && (
        <div className="fact">
          <h2>Fun Fact:</h2>
          <p>{fact}</p>
        </div>
      )}
    </div>
  );
};

export default PlantRecognitionApp;
