import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import PlantRecognitionApp from './PlantRecognition';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
    <PlantRecognitionApp />
  </React.StrictMode>
);
