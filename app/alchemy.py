from sqlalchemy import create_engine, Column, Float, Integer, String, DateTime,Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import datetime

DATABASE_URL = "postgresql://postgres:password@localhost:5432/dsp23"

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

db = SessionLocal()
db_prediction = PredictionRecord(
    id = 3,
    TotRmsAbvGrd = 1.0,
    WoodDeckSF = 1.0,
    YrSold = 2023,
    FirstFlrSF = 1.0,
    Foundation_BrkTil = 1,
    Foundation_CBlock = 0,
    Foundation_PConc = 0,
    Foundation_Slab = 0,
    Foundation_Stone = 0,
    Foundation_Wood = 0,
    KitchenQual_Ex = 0,
    KitchenQual_Fa = 1,
    KitchenQual_Gd = 0,
    KitchenQual_TA = 0,
    # predict_date = datetime.date.today(),
    predict_date = datetime.now(),
    predict_result = 200303.0,
    predict_source = "web",
    )
db.add(db_prediction)
db.commit()
db.refresh(db_prediction)
   
