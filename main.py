from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from starlette.requests import Request
import uvicorn

app = FastAPI()
DATABASE_URL = "postgresql://postgres:admin@localhost"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String)
    message = Column(String)
    resourceId = Column(String)
    timestamp = Column(DateTime)
    traceId = Column(String)
    spanId = Column(String)
    commit = Column(String)
    parentResourceId = Column(String)

class LogIn(BaseModel):
    level: str
    message: str
    resourceId: str
    timestamp: str
    traceId: str
    spanId: str
    commit: str
    metadata: dict

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_instance():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/")
async def ingest_stream(request: Request, db: Session = Depends(get_db_instance)):
    async for chunk in request.stream():
        data = chunk.decode()  # decode bytes to string
        # Process the JSON data here. This could be any kind of processing depending on your needs.
        db_logs = [Log(**log.dict()) for log in data]
        db.add_all(db_logs)
        print(type(data))
        db.commit()
        db.refresh(data)

    return {"msg": "Data processed successfully"}




if __name__ == '__main__':
    uvicorn.run(app, port=3000, workers=5)