import joblib

model = joblib.load("data\\housepricing.joblib")
pred = model.predict([[-0.953400,-0.759146,0.133716,0.080426,0,0,1,0,0,0,0,0,1,0]])
print(pred)