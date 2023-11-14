from fastapi import FastAPI,UploadFile
from pydantic import BaseModel
import joblib
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, Column, Float, Integer, String, DateTime, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import io
from typing import List,Union

app = FastAPI()

model = joblib.load("..\\data\\housepricing.joblib")

pw = ""
############################################### DATABASE CONNECTION ###########################################

DATABASE_URL = "postgresql://postgres:password@localhost:5432/dsp23"


engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
###############################################################################################################

################################################## Postgres Table class ######################################
class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, nullable=False)
    TotRmsAbvGrd = Column(Integer)
    WoodDeckSF = Column(Integer)
    YrSold = Column(Integer)
    FirstFlrSF = Column(Integer)
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
    TotRmsAbvGrd: int
    WoodDeckSF: int
    YrSold: int
    FirstFlrSF: int
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
class FileData(BaseModel):
    file: Union[List[List[int]],InputData]
##############################################################################################################

class PastPredictionData(BaseModel):
    start_date: str 
    end_date: str
    prediction_source: str 

########################################## Single prediction endpoint ########################################
@app.post("/predict")
async def predict(data: FileData):
    if isinstance(data.file, InputData):
        input_data = [
            data.file.TotRmsAbvGrd,
            data.file.WoodDeckSF,
            data.file.YrSold,
            data.file.FirstFlrSF,
            data.file.Foundation_BrkTil,
            data.file.Foundation_CBlock,
            data.file.Foundation_PConc,
            data.file.Foundation_Slab,
            data.file.Foundation_Stone,
            data.file.Foundation_Wood,
            data.file.KitchenQual_Ex,
            data.file.KitchenQual_Fa,
            data.file.KitchenQual_Gd,
            data.file.KitchenQual_TA
        ]
        
        prediction = model.predict([input_data])

        db = SessionLocal()
        db_prediction = PredictionRecord(
            TotRmsAbvGrd=data.file.TotRmsAbvGrd,
            WoodDeckSF=data.file.WoodDeckSF,
            YrSold=data.file.YrSold,
            FirstFlrSF=data.file.FirstFlrSF,
            Foundation_BrkTil=data.file.Foundation_BrkTil,
            Foundation_CBlock=data.file.Foundation_CBlock,
            Foundation_PConc=data.file.Foundation_PConc,
            Foundation_Slab=data.file.Foundation_Slab,
            Foundation_Stone=data.file.Foundation_Stone,
            Foundation_Wood=data.file.Foundation_Wood,
            KitchenQual_Ex=data.file.KitchenQual_Ex,
            KitchenQual_Fa=data.file.KitchenQual_Fa,
            KitchenQual_Gd=data.file.KitchenQual_Gd,
            KitchenQual_TA=data.file.KitchenQual_TA,
            predict_date=datetime.now(),
            predict_result=round(prediction[0], 2),
            predict_source="web",
        )
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)

        return {"predictions": prediction[0], "data": input_data}
    
    elif isinstance(data.file, List):
        predictions = model.predict(data.file)
        predictions_list = predictions.tolist()

        column_names = ["TotRmsAbvGrd", "WoodDeckSF", "YrSold", "FirstFlrSF", "Foundation_BrkTil",
                        "Foundation_CBlock", "Foundation_PConc", "Foundation_Slab", "Foundation_Stone",
                        "Foundation_Wood", "KitchenQual_Ex", "KitchenQual_Fa", "KitchenQual_Gd", "KitchenQual_TA"]

        df = pd.DataFrame(data.file, columns=column_names)

        df["predict_date"] = datetime.now()
        df["predict_result"] = predictions_list
        df["predict_source"] = "web"

        data_dict = df.to_dict(orient="records")

        db = SessionLocal()
        db.bulk_insert_mappings(PredictionRecord, data_dict)
        db.commit()

        return {"predictions": predictions_list, "original_data": data_dict}

################################### Get Past Predictions# ########################################
@app.get("/past-predictions")
async def get_predictions(data: PastPredictionData):
    start_date = f"{data.start_date} 00:00:00"
    end_date = f"{data.end_date} 00:00:00"
    prediction_source = data.prediction_source

    statement = select(PredictionRecord.TotRmsAbvGrd,
                       PredictionRecord.WoodDeckSF,
                       PredictionRecord.YrSold,
                       PredictionRecord.FirstFlrSF,
                       PredictionRecord.predict_date,
                       PredictionRecord.predict_source,
                       PredictionRecord.predict_result
                       ).where(
        PredictionRecord.predict_date >= start_date,
        PredictionRecord.predict_date <= end_date
        )
    if prediction_source != 'all':
        statement = statement.where(
            PredictionRecord.predict_source == prediction_source)

    db = SessionLocal()
    result = db.execute(statement)

    return result.mappings().all()
##########################################################################################################
# if __name__ == "__main__":
#     uvicorn.run("main_api:app", host="127.0.0.1", port=8000)
