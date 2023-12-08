from sqlalchemy import create_engine, Column, String, Integer, TIMESTAMP, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

pw = 'postgres'
DATABASE_URL = "postgresql://postgres:"+pw+"@localhost:5432/dsp23"
Base = declarative_base()


class DataError(Base):
    __tablename__ = 'data_errors'

    id = Column(Integer, primary_key=True, index=True)
    dag_run_date = Column(TIMESTAMP, nullable=False)
    file_name = Column(String(255), nullable=False)
    description = Column(Text)


engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def save_data_errors(file_name, description):
    db = SessionLocal()

    current_date = datetime.now()
    formatted_date = current_date.strftime('%Y-%m-%d %H:%M:%S')

    data_error = DataError(dag_run_date=formatted_date,
                           file_name=file_name, description=description)
    db.add(data_error)
    db.commit()
    db.refresh(data_error)

    db.close()
