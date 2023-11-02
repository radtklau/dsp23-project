from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
from datetime import datetime
import psycopg2
from sqlalchemy import create_engine, Column, Float, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

app = FastAPI()

# Load the saved joblib model
model = joblib.load("data\\housepricing.joblib")

##
DATABASE_URL = "postgresql://postgres:Loyaldreambalde11@localhost:5432/dsp23"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, nullable=False)
    TotRmsAbvGrd = Column(Float)
    WoodDeckSF = Column(Float)
    YrSold = Column(Integer)
    FirstFlrSF = Column(Float)
    Foundation_BrkTil = Column(Integer)
    Foundation_CBlock = Column(Integer)
    Foundation_PConc = Column(Integer)
    Foundation_Slab = Column(Integer)
    Foundation_Stone = Column(Integer)
    Foundation_Wood = Column(Integer)
    KitchenQual_Ex = Column(Integer)
    KitchenQual_Fa = Column(Integer)
    KitchenQual_Gd = Column(Integer)
    KitchenQual_TA = Column(Integer)
    predict_date = Column(DateTime, default=datetime.utcnow)
    predict_result = Column(Float)
    predict_source = Column(String(4))

# Data Validation with Pydandic.BaseModel
class InputData(BaseModel):
    TotRmsAbvGrd: float
    WoodDeckSF: float
    YrSold: int
    FirstFlrSF: float
    Foundation_BrkTil: int
    Foundation_CBlock: int
    Foundation_PConc: int
    Foundation_Slab: int
    Foundation_Stone: int
    Foundation_Wood: int
    KitchenQual_Ex: int
    KitchenQual_Fa: int
    KitchenQual_Gd: int
    KitchenQual_TA: int
    
# The predict Path function
@app.post("/predict")
def predict(data: InputData):
    # Preparing the prediction data received from the streamlit UI
    input_data = [
        data.TotRmsAbvGrd,
        data.WoodDeckSF,
        data.YrSold,
        data.FirstFlrSF,
        data.Foundation_BrkTil,
        data.Foundation_CBlock,
        data.Foundation_PConc,
        data.Foundation_Slab,
        data.Foundation_Stone,
        data.Foundation_Wood,
        data.KitchenQual_Ex,
        data.KitchenQual_Fa,
        data.KitchenQual_Gd,
        data.KitchenQual_TA
    ]
    
    # Make prediction with the loaded model and 
    # the data we received from the streamlit UI
    prediction = model.predict([input_data])

    # Enregistrez la prédiction dans la base de données PostgreSQL
    db = SessionLocal()
    db_prediction = PredictionRecord(
        # id = 5,
        TotRmsAbvGrd = data.TotRmsAbvGrd,
        WoodDeckSF = data.WoodDeckSF,
        YrSold = data.YrSold,
        FirstFlrSF = data.FirstFlrSF,
        Foundation_BrkTil = data.Foundation_BrkTil,
        Foundation_CBlock = data.Foundation_CBlock,
        Foundation_PConc = data.Foundation_PConc,
        Foundation_Slab = data.Foundation_Slab,
        Foundation_Stone = data.Foundation_Stone,
        Foundation_Wood = data.Foundation_Wood,
        KitchenQual_Ex = data.KitchenQual_Ex,
        KitchenQual_Fa = data.KitchenQual_Fa,
        KitchenQual_Gd = data.KitchenQual_Gd,
        KitchenQual_TA = data.KitchenQual_TA,
        # predict_date = datetime.date.today(),
        predict_date = datetime.now(),
        predict_result = prediction[0],
        predict_source = "web",
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)

    # return the prediction value to the streamlit UI
    return {"predictions": prediction[0],"data":input_data}
