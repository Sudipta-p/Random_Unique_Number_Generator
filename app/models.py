from sqlalchemy import Column, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UsedNumber(Base):
    __tablename__ = "used_numbers"
    
    number = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UsedNumber(number={self.number})>" 