import json
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
    try:
        async for chunk in request.stream():
            data = json.loads(chunk.decode())
            db_logs = [Log(**log) for log in data]
            print(len(db_logs))
            db.add_all(db_logs)
            db.commit()
    except Exception as e:
        print(e)
    return {"msg": "Data processed successfully"}


@app.get("/search")
@app.get("/search/{attribute}/")
async def search(q:str, attribute:str | None, db:Session = Depends(get_db_instance)):
    attribute = getattr(Log, attribute, None)
    if attribute:
        results = db.query(Log).filter(attribute.like(f"%{q}%")).all()
        return results
    else:
        results = db.query(Log).filter(Log.commit.like(f"%{q}%")).all()
    


if __name__ == '__main__':
    uvicorn.run(app, port=3000, workers=5)