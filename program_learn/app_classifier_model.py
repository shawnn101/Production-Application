import pandas as pd
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

# Load your labeled data
df = pd.read_csv("app_classification_data.csv")

# Create a pipeline: vectorizer + classifier
pipeline = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# Train the model
pipeline.fit(df['AppName'], df['Category'])

# Save the model
joblib.dump(pipeline, "app_classifier_model.pkl")
print("✅ app_classifier_model.pkl saved.")
