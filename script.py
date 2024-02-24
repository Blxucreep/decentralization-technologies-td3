# script.py
import numpy as np
import pandas as pd
import requests
from collections import defaultdict
from sklearn.metrics import f1_score

# Load the data
df = pd.read_csv('titanic_cleaned.csv')

# Create a list of models
models = ['knn', 'svc', 'decision_tree', 'random_forest', 'gradient_boosting']

# Define the base URL for the Flask API
base_url = 'http://127.0.0.1:5000'

# Function to load a model from a remote server
def load_model(model_name):
    try:
        model_url = f'{base_url}/predict?model={model_name}'
        return model_url
    except Exception as e:
        print(f"Error loading the model: {str(e)}.")
        return None

# Function to make predictions using a remote model
def make_prediction(model_url, features):
    try:
        response = requests.get(model_url, params={f: features[i] for i, f in enumerate(['pclass', 'age', 'sibsp', 'parch', 'fare', 'alone', 'sex_male', 'embarked_Q', 'embarked_S', 'class_Second', 'class_Third', 'embark_town_Queenstown', 'embark_town_Southampton'])})
        prediction = response.json().get('prediction')
        return prediction
    except Exception as e:
        print(f"Prediction failed: {str(e)}")
        return None
# Function to calculate accuracy of a model
def accuracy_of_model(model_name, prediction):
    if model_name in df.columns:
        return np.mean(prediction == df[model_name])
    else:
        print(f"Model {model_name} not found in DataFrame columns.")
        return None



# Function to calculate F1 score of a model
def f1_of_model(model_name, prediction):
    return f1_score(df[model_name], prediction, average='binary', labels=np.unique(prediction))
# Function to calculate model weights based on accuracy
def calculate_model_weights(models, consensus_prediction, model_weights):
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
                # Calculate the model accuracy
                model_accuracy = accuracy_of_model(model_name, prediction)

                # Update model weights
                if model_accuracy is not None:
                    model_weights[model_name] += model_accuracy

    total_weight = sum(model_weights.values())

    if total_weight == 0:
        # Assign equal weights to all models if the total weight is zero
        model_weights = {model_name: 1 / len(models) for model_name in models}
    else:
        # Normalize weights
        model_weights = {model_name: weight / total_weight for model_name, weight in model_weights.items()}

    return model_weights



# Q2: Evaluate the accuracy and performance of each model.
for model_name in models:
    model_url = load_model(model_name)

    if model_url:
        sample_features = [1, 25, 1, 0, 50, 0, 1, 0, 1, 0, 0, 0, 1]
        prediction = make_prediction(model_url, sample_features)

        if prediction:
            model_accuracy = accuracy_of_model(model_name, prediction)
            print(f"Model {model_name} Accuracy: {model_accuracy}")

# Q4: Introduce a weighting system to refine the meta-model's predictions.
# Q5: Implement a proof-of-stake consensus mechanism with a slashing protocol.

# Simulating a slashing scenario (for demonstration purposes)
slashing_threshold = 0.7  # Adjust the threshold based on your requirements

# Initialize an empty list to store individual predictions
individual_predictions = []

# Loop through each model and make predictions
for model_name in models:
    # Load the model
    model_url = load_model(model_name)

    if model_url:
        sample_features = [1, 25, 1, 0, 50, 0, 1, 0, 1, 0, 0, 0, 1]
        prediction = make_prediction(model_url, sample_features)

        if prediction:
            individual_predictions.append(prediction)

# Calculate the consensus prediction by averaging individual predictions
consensus_prediction = np.mean(individual_predictions)

# Print the consensus and weighted consensus predictions
print(f"Consensus Prediction: {consensus_prediction}")
if not np.isnan(consensus_prediction):
    # Calculate model weights based on F1 score
    model_weights = defaultdict(float)
    model_weights = calculate_model_weights(models, consensus_prediction, model_weights)
    
    # Print the model weights
    print("Model Weights:", model_weights)

    # Calculate the weighted consensus prediction
    weighted_consensus_prediction = np.average(np.array(individual_predictions), weights=list(model_weights.values()), axis=0)
    print(f"Weighted Consensus Prediction: {weighted_consensus_prediction}")
else:
    print("All models have been slashed. No consensus prediction available.")
