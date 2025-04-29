import random
from sqlalchemy.orm import Session
from typing import Optional
from . import models

class NumberGeneratorService:
    def __init__(self, db: Session):
        self.db = db
        self._min_number = 1
        self._max_number = 1_000_000  # Adjust range as needed
        
    def _number_exists(self, number: int) -> bool:
        """Check if a number has been used before."""
        return self.db.query(models.UsedNumber).filter(
            models.UsedNumber.number == number
        ).first() is not None
    
    def generate_unique_number(self) -> Optional[int]:
        """Generate a unique random number that hasn't been used before."""
        # Get count of used numbers
        used_count = self.db.query(models.UsedNumber).count()
        
        # If all numbers in range are used, return None
        if used_count >= (self._max_number - self._min_number + 1):
            return None
            
        while True:
            number = random.randint(self._min_number, self._max_number)
            if not self._number_exists(number):
                # Save the number as used
                used_number = models.UsedNumber(number=number)
                self.db.add(used_number)
                self.db.commit()
                return number 