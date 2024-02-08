# Q2: Generate a consensus prediction by averaging outputs from the group's models, using tools like ngrok for inter-computer connectivity. Assess the performance of this aggregated meta-model.
# This stage illustrates the creation of a distributed prediction system in a trusted environment. The next step involves opening the model to external contributions, which may come from both benign and malicious actors.

# import libraries
import numpy as np
import pandas as pd

# load the data
df = pd.read_csv('titanic_cleaned.csv')

# create a list of models
models = ['knn', 'svc', 'decision_tree', 'random_forest', 'gradient_boosting']

# separate the features and the target variable
X = df.drop('survived', axis=1)
y = df['survived']