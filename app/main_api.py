from fastapi import FastAPI,UploadFile
from pydantic import BaseModel
import joblib
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Float, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import io

app = FastAPI()

# Load the saved joblib model
model = joblib.load("..\\data\\housepricing.joblib")

############################################### DATABASE CONNECTION ###########################################
DATABASE_URL = "postgresql://postgres:Loyaldreambalde11@localhost:5432/dsp23"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
###############################################################################################################

################################################## Postgres Table class ######################################
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
##############################################################################################################

##################################### Data Validation with Pydandic.BaseModel ################################
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
##############################################################################################################

########################################## Single prediction endpoint ########################################
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
        predict_date = datetime.now(),
        predict_result = round(prediction[0],2),
        predict_source = "web",
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)

    # return the prediction value to the streamlit UI
    return {"predictions": prediction[0],"data":input_data}

##########################################################################################################


################################### Multiple prediction endpoint #########################################
@app.post("/predict_csv")
async def predict(file: UploadFile):
    file_contents = file.file.read()

    # Convertir le contenu en DataFrame
    data = pd.read_csv(io.StringIO(file_contents.decode("utf-8")))

    # Effectuer des prédictions avec le modèle
    predictions = model.predict(data)

    predictions_list = predictions.tolist()
    data["predict_date"] = datetime.now()
    data["predict_result"] = predictions_list
    data["predict_source"] = "web"

    # transform the dataframe to a dict just to insert it into the DB
    data_dict = data.to_dict(orient="records")

    # bulk_insert_mappings will insert all the dict into the DB at the same time
    db = SessionLocal()
    db.bulk_insert_mappings(PredictionRecord, data_dict)
    db.commit()
    
    # return the predictions to the streamlit UI
    return {"predictions": predictions_list}
###########################################################################################################
    