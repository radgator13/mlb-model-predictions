import joblib

model = joblib.load("ou_model.pkl")
print("Model type:", type(model))
