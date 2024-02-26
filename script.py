import numpy as np
import pandas as pd
import requests
import json
import os

# Load the data
df = pd.read_csv('titanic_cleaned.csv')

# Create a list of models
models = ['knn', 'svc', 'decision_tree', 'random_forest', 'gradient_boosting']

# Define the base URL for Ngrok, assuming Ngrok is running on port 4040
base_url = 'http://127.0.0.1:4040'

# Function to load a model from a remote server
def load_model(model_name):
    try:
        model_url = f'{base_url}/api/tunnels/{model_name}/predict'
        return model_url
    except Exception as e:
        print(f"Error loading the model: {str(e)}.")
        return None

# Function to make predictions using a remote model
def make_prediction(model_url, features):
    try:
        response = requests.get(model_url, params=features)
        prediction = response.json().get('prediction')
        return prediction
    except Exception as e:
        print(f"Prediction failed: {str(e)}")
        return None

# Function to calculate accuracy of a model
def accuracy_of_model(model_name, consensus_prediction):
    return np.mean(consensus_prediction == df[model_name])

# Function to calculate model weights based on accuracy
def calculate_model_weights(models, consensus_prediction):
    model_weights = {model_name: accuracy_of_model(model_name, consensus_prediction) for model_name in models if model_name in df.columns}
    total_weight = sum(model_weights.values())

    if total_weight == 0:
        # Assign equal weights to all models if total weight is zero
        model_weights = {model_name: 1 / len(models) for model_name in models}
    else:
        # Normalize weights
        model_weights = {model_name: weight / total_weight if total_weight != 0 else 0 for model_name, weight in model_weights.items()}

    return model_weights

# Q4: Introduce a weighting system to refine the meta-model's predictions.
# Weights are adjusted with each prediction batch to reflect the accuracy of individual models.

# Q5: Implement a proof-of-stake consensus mechanism with a slashing protocol.
# Models must make an initial deposit upon registration to participate.
# This deposit serves as a security measure, ensuring participants' commitment to the network's integrity.

# Implement penalties (slashing) for actions that undermine network accuracy or trustworthiness.
# For example, consistently inaccurate predictions may result in a loss of deposit.

# Simulating a slashing scenario (for demonstration purposes)
slashing_threshold = 0.7  # Adjust the threshold based on your requirements

# Check model accuracy against the slashing threshold
model_weights = calculate_model_weights(models, np.zeros(len(df)))  # Initialize with zero consensus prediction
slashing_results = {model_name: accuracy < slashing_threshold for model_name, accuracy in model_weights.items()}

# Apply slashing penalties (for simplicity, reduce the model weight to zero for models that violate the threshold)
for model_name, slashed in slashing_results.items():
    if slashed:
        model_weights[model_name] = 0

# Normalize weights after potential slashing
total_weight = sum(model_weights.values())
model_weights = {model_name: weight / total_weight if total_weight != 0 else 0 for model_name, weight in model_weights.items()}

# Track model balances in a JSON database (assuming a simple local database)
json_db_path = 'model_balances.json'

# Initialize model balances if the JSON database doesn't exist
if not os.path.exists(json_db_path):
    model_balances = {model_name: 1000 for model_name in models}  # Initial deposit of 1000 euros
else:
    # Load existing model balances from the JSON database
    with open(json_db_path, 'r') as json_file:
        model_balances = json.load(json_file)

# Update model balances based on model weights
for model_name, weight in model_weights.items():
    model_balances[model_name] += weight * 100  # Assuming 100 euros per prediction

# Save updated model balances to the JSON database
with open(json_db_path, 'w') as json_file:
    json.dump(model_balances, json_file)

# Only calculate consensus prediction if at least one model is not slashed
if np.any(list(model_weights.values())):
    # Initialize an empty list to store individual predictions
    individual_predictions = []

    # Loop through each model and make predictions
    for model_name in models:
        # Load the model
        model_url = load_model(model_name)

        if model_url:
            # Make a sample prediction (you can replace this with your actual feature values)
            sample_features = {
                'pclass': 1,
                'age': 25,
                'sibsp': 1,
                'parch': 0,
                'fare': 50,
                'alone': 0,
                'sex_male': 1,
                'embarked_Q': 0,
                'embarked_S': 1,
                'class_Second': 0,
                'class_Third': 0,
                'embark_town_Queenstown': 0,
                'embark_town_Southampton': 1
            }

            # Make a prediction using the current model
            prediction = make_prediction(model_url, sample_features)

            if prediction:
                # Append the prediction to the list
                individual_predictions.append(prediction)

    # Calculate the consensus prediction by averaging individual predictions
    consensus_prediction = np.mean(individual_predictions)

    # Print the consensus, weighted consensus predictions, and model balances
    print(f"Consensus Prediction: {consensus_prediction}")
    if not np.isnan(consensus_prediction):
        weighted_consensus_prediction = np.average(np.array(individual_predictions).reshape(-1, 1), weights=list(model_weights.values()))
        print(f"Weighted Consensus Prediction: {weighted_consensus_prediction}")
else:
    print("All models have been slashed. No consensus prediction available.")

print("Model Balances:", model_balances)
