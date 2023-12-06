from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from datetime import datetime 


pw = ''
DATABASE_URL = "postgresql://postgres:"+pw+"@localhost:5432/testdb"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def save_data_errors(file_name, description):
    table = 'data_errors' 
    
    current_date = datetime.now()
    formatted_date = current_date.strftime('%Y-%m-%d %H:%M:%S')

    statement = insert(table).values(dag_run_date=formatted_date,
                                     file_name=file_name,
                                     description=description)

    db = SessionLocal()
    result = db.execute(statement)
    return result



save_data_errors('testfile.csv','desc test ajfkdlsfsaklfhgsagjçkslgjsakldfjdsaçlfsa')
