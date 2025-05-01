from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from . import models, database, services

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Unique Random Number Server",
    description="A service that generates unique random numbers that are never repeated",
    version="1.0.0"
)

@app.get("/random", response_model=Dict[str, int])
def get_random_number(db: Session = Depends(database.get_db)):
    """
    Get a unique random number that has never been returned before.
    The number will be generated using various mathematical functions and strategies
    to ensure uniqueness and handle exhausted ranges.
    """
    service = services.NumberGeneratorService(db)
    number = service.generate_unique_number()
    
    if number is None:
        raise HTTPException(
            status_code=503,
            detail="All available numbers in the range have been used"
        )
    
    return {"number": number}

@app.get("/health")
def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy"} 