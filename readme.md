# **📦 Carbon Footprint Optimization for Logistics**

This project implements a web application using **Streamlit** to estimate the carbon emissions (CO₂) for individual logistics and delivery routes. It integrates machine learning (a pre-trained **Random Forest Regressor**) with real-time route optimization using the **OpenRouteService API** to provide data-driven insights for eco-friendly logistics planning.

## **🚀 Key Features**

* **Real-Time Route Analysis:** Uses location data (from a Nominatim search) to calculate the actual driving distance, duration, and route map via the OpenRouteService API.  
* **Machine Learning Prediction:** Employs a trained model (carbon\_emission\_model.pkl) to predict the expected CO₂ emissions (in kg) based on factors like distance, cargo weight, vehicle type, and traffic/weather conditions.  
* **Cost Estimation:** Calculates the estimated fuel cost (in INR) for the route.  
* **Multi-Delivery Dashboard:** Tracks and visualizes metrics (CO₂, cost, distance, time) for multiple predictions made during a session.  
* **Data Export:** Allows users to download single delivery records or the entire session dashboard as a CSV file.

## **🛠️ Project Structure**

| File | Description |
| :---- | :---- |
| app.py | The main Streamlit application file. Contains the UI, API integration logic (ORS, OpenWeatherMap), ML model prediction, and dashboard display. |
| carbon\_model\_training.ipynb | Jupyter Notebook detailing the data loading, preprocessing (Label Encoding), model training (Random Forest Regressor), and saving of the final model. |
| carbon\_logistics\_dataset.csv | The raw dataset used to train the ML model. It includes features like Distance\_km, Cargo\_Weight\_kg, Vehicle\_Type, and the target variable CO2\_Emission\_kg. |
| carbon\_emission\_model.pkl | The trained **RandomForestRegressor** model, serialized using joblib. This model is loaded directly by app.py for inference. |
| requirements.txt | Lists all necessary Python dependencies (including streamlit, scikit-learn, openrouteservice, etc.) required to run the application. |

## **⚙️ Setup and Installation**

### **1\. Prerequisites**

You must have **Python 3.8+** installed on your system.

### **2\. Clone the Repository (Simulated Step)**

Assuming all files are in a single directory:

\# Navigate to your project folder  
cd carbon-logistics-optimizer

### **3\. Install Dependencies**

Install all required Python libraries using the provided requirements.txt file.

pip install \-r requirements.txt

### **4\. API Key Configuration (Crucial Step)**

The application relies on two external APIs. The provided keys in app.py are placeholders or examples. **You must replace them with your own valid keys.**

1. **OpenRouteService (ORS) API:**  
   * Sign up at [https://openrouteservice.org/](https://openrouteservice.org/).  
   * Replace the placeholder value for ORS\_API\_KEY in app.py.  
2. **OpenWeatherMap API:**  
   * Sign up at [https://openweathermap.org/](https://openweathermap.org/).  
   * Replace the placeholder value for WEATHER\_API\_KEY in app.py.

In app.py, locate and update these lines:

ORS\_API\_KEY \= "YOUR\_OPENROUTESERVICE\_API\_KEY\_HERE"  
WEATHER\_API\_KEY \= "YOUR\_OPENWEATHERMAP\_API\_KEY\_HERE"

## **🏃 How to Run the Application**

Once the dependencies are installed and the API keys are configured, run the Streamlit application from your terminal:

streamlit run app.py

The application will automatically open in your web browser (usually at http://localhost:8501).

## **📝 Model Training Details**

The machine learning model was trained using the following process, detailed in carbon\_model\_training.ipynb:

* **Model Type:** Random Forest Regressor.  
* **Target Variable:** CO2\_Emission\_kg.  
* **Features:** Distance\_km, Traffic (0-2), Cargo\_Weight\_kg, Weather (0/1), Vehicle\_Type (Label Encoded), and Delivery\_Time\_min.  
* **Evaluation:** The model achieved a **Mean Absolute Error (MAE) of approximately 4.01 kg CO₂** on the test set, indicating a reasonable accuracy for emission estimation.