# File: log_ingestor.py

from fastapi import FastAPI, HTTPException, Query, Request, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi import Depends
from fastapi import Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# PostgreSQL database configuration
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

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LogEntry(BaseModel):
    level: str
    message: str
    resourceId: str
    timestamp: str
    traceId: str
    spanId: str
    commit: str
    metadata: dict

@app.get("/",  response_model=None)
async def root():
    return RedirectResponse("/docs")

# Log ingestion endpoint
@app.post("/ingest", response_model=None)
async def ingest_log(log_entry: Log, db: Session = Depends(get_db)):
    # Exclude the 'id' field when creating a new log entry
    db_log = Log(
        level=log_entry.level,
        message=log_entry.message,
        resourceId=log_entry.resourceId,
        timestamp=log_entry.timestamp,
        traceId=log_entry.traceId,
        spanId=log_entry.spanId,
        commit=log_entry.commit,
        parentResourceId=log_entry.metadata.get("parentResourceId")
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# Search logs endpoint
@app.get("/search", response_class=HTMLResponse)
async def search_logs(
    request: Request,
    level: Optional[str] = Query(None, title="Log Level"),
    message: Optional[str] = Query(None, title="Log Message"),
    resourceId: Optional[str] = Query(None, title="Resource ID"),
    timestamp: Optional[str] = Query(None, title="Timestamp"),
    traceId: Optional[str] = Query(None, title="Trace ID"),
    spanId: Optional[str] = Query(None, title="Span ID"),
    commit: Optional[str] = Query(None, title="Commit"),
    parentResourceId: Optional[str] = Query(None, title="Parent Resource ID (Metadata)"),
    db: Session = Depends(get_db)
):
    # Filter logs based on provided parameters
    filtered_logs = filter_logs(
        db, level=level, message=message, resourceId=resourceId,
        timestamp=timestamp, traceId=traceId, spanId=spanId,
        commit=commit, parentResourceId=parentResourceId
    )

    return templates.TemplateResponse("search_logs.html", {"request": request, "logs": filtered_logs})

# Helper function to filter logs based on provided parameters
def filter_logs(db, **kwargs):
    query = db.query(Log)
    for key, value in kwargs.items():
        if value is not None:
            query = query.filter(getattr(Log, key) == value)
    return query.all()

if __name__ == "__main__":
    import uvicorn
    from sqlalchemy.orm import Session

    # Run the FastAPI application on port 3000
    uvicorn.run(app, host="127.0.0.1", port=3000, reload=True)
