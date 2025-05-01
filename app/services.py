import random
from sqlalchemy.orm import Session
from typing import Optional, Union
from . import models

class NumberGeneratorService:
    def __init__(self, db: Session):
        self.db = db
        self._min_number = 1
        self._max_number = 1_000_000  # Adjust range as needed
        
    def _number_exists(self, number: Union[int, float]) -> bool:
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

    def generate_random_number(self, number_type: str = 'int', min_val: float = 0, max_val: float = 100, 
                             precision: int = 2) -> Union[int, float]:
        """
        Generate a random number that can be either integer or float.
        
        Args:
            number_type (str): Type of number to generate ('int' or 'float')
            min_val (float): Minimum value (inclusive)
            max_val (float): Maximum value (inclusive)
            precision (int): Number of decimal places for float (default: 2)
            
        Returns:
            Union[int, float]: Random number of specified type
        """
        if number_type.lower() == 'int':
            return random.randint(int(min_val), int(max_val))
        elif number_type.lower() == 'float':
            # Generate float with specified precision
            random_float = random.uniform(min_val, max_val)
            return round(random_float, precision)
        else:
            raise ValueError("number_type must be either 'int' or 'float'")

    def generate_unbounded_random(self, number_type: str = 'int', precision: int = 2) -> Union[int, float]:
        """
        Generate a random number without range constraints.
        
        Args:
            number_type (str): Type of number to generate ('int' or 'float')
            precision (int): Number of decimal places for float (default: 2)
            
        Returns:
            Union[int, float]: Random number of specified type
        """
        if number_type.lower() == 'int':
            # Generate a random integer using random.getrandbits
            # This will generate a random integer with up to 32 bits
            return random.getrandbits(32)
        elif number_type.lower() == 'float':
            # Generate a random float between 0 and 1, then scale it
            # This will give us a random float with the specified precision
            random_float = random.random()
            return round(random_float, precision)
        else:
            raise ValueError("number_type must be either 'int' or 'float'") 