import random
import math
from sqlalchemy.orm import Session
from typing import Optional, Union, List, Callable, Tuple
from . import models
import time

class NumberGeneratorService:
    def __init__(self, db: Session):
        self.db = db
        self._default_min = -1_000_000
        self._default_max = 1_000_000
        self._max_expansions = 3
        self._expansion_factor = 2
        # Initialize available generation methods
        self.generation_methods = [
            self.generate_random_number,
            self.generate_unbounded_random,
            self.generate_math_random
        ]
        
    def _number_exists(self, number: Union[int, float]) -> bool:
        """Check if a number has been used before."""
        return self.db.query(models.UsedNumber).filter(
            models.UsedNumber.number == number
        ).first() is not None
    
    def _save_number(self, number: Union[int, float]) -> None:
        """Save a used number to the database"""
        used_number = models.UsedNumber(number=number)
        self.db.add(used_number)
        self.db.commit()

    def _expand_range(self, min_val: int, max_val: int) -> tuple[int, int]:
        """Expand the range by a factor"""
        range_size = max_val - min_val
        new_min = min_val - (range_size * (self._expansion_factor - 1) // 2)
        new_max = max_val + (range_size * (self._expansion_factor - 1) // 2)
        return new_min, new_max

    def _get_available_range(self, min_val: int, max_val: int) -> tuple[int, int]:
        """Get the actual available range by checking the database"""
        used_numbers = self.db.query(models.UsedNumber).filter(
            models.UsedNumber.number >= min_val,
            models.UsedNumber.number <= max_val
        ).all()
        
        used_set = {n.number for n in used_numbers}
        available = set(range(min_val, max_val + 1)) - used_set
        
        if not available:
            return min_val, max_val  # Return original range if no numbers available
            
        return min(available), max(available)

    def _is_range_exhausted(self, min_val: int, max_val: int) -> bool:
        """Check if a range is completely exhausted"""
        count = self.db.query(models.UsedNumber).filter(
            models.UsedNumber.number >= min_val,
            models.UsedNumber.number <= max_val
        ).count()
        return count >= (max_val - min_val + 1)

    def _handle_exhausted_range(self, min_val: int, max_val: int) -> tuple[int, int]:
        """Handle an exhausted range by clearing the database and expanding the range"""
        # Clear all numbers in the current range
        self.clear_used_numbers(min_val, max_val)
        
        # Expand the range
        for _ in range(self._max_expansions):
            min_val, max_val = self._expand_range(min_val, max_val)
            if not self._is_range_exhausted(min_val, max_val):
                return min_val, max_val
                
        # If we've exhausted all expansions, clear the entire database and start fresh
        self.clear_used_numbers()
        return self._default_min, self._default_max

    def generate_unique_number(self) -> Optional[int]:
        """
        Generate a unique random number using various strategies.
        All range handling and expansion is done internally.
        """
        min_val, max_val = self._default_min, self._default_max
        
        # Check if current range is exhausted
        if self._is_range_exhausted(min_val, max_val):
            min_val, max_val = self._handle_exhausted_range(min_val, max_val)

        # Get actual available range
        min_val, max_val = self._get_available_range(min_val, max_val)
        
        # Try different generation methods
        methods = [
            self._generate_math_random,
            self._generate_math_sequence,
            self._generate_math_range,
            self._generate_unbounded_random
        ]
        
        # Shuffle methods for variety
        random.shuffle(methods)
        
        for method in methods:
            try:
                number = method(min_val, max_val)
                if number is not None and not self._number_exists(number):
                    self._save_number(number)
                    return number
            except Exception:
                continue
        
        return None

    def _generate_math_random(self, min_val: int, max_val: int) -> Optional[int]:
        """Generate a random number using mathematical functions"""
        try:
            # Use current timestamp as part of the seed
            seed = int(time.time() * 1000)
            random.seed(seed)
            
            # Try different mathematical approaches
            approaches = [
                lambda: int(math.sin(seed) * (max_val - min_val) + min_val),
                lambda: int(math.cos(seed) * (max_val - min_val) + min_val),
                lambda: int(math.tan(seed) * (max_val - min_val) + min_val),
                lambda: int(math.exp(seed % 10) * (max_val - min_val) / 100 + min_val),
                lambda: int(math.log(abs(seed) + 1) * (max_val - min_val) / 10 + min_val)
            ]
            
            # Try each approach until we get a valid number
            for approach in approaches:
                try:
                    number = approach()
                    if min_val <= number <= max_val:
                        return number
                except Exception:
                    continue
                    
            return None
        except Exception:
            return None

    def _generate_math_sequence(self, min_val: int, max_val: int) -> Optional[int]:
        """Generate a number using mathematical sequences"""
        try:
            seed = int(time.time() * 1000)
            random.seed(seed)
            
            # Try different sequence approaches
            approaches = [
                lambda: int(min_val + (seed % (max_val - min_val + 1))),
                lambda: int(max_val - (seed % (max_val - min_val + 1))),
                lambda: int(min_val + ((seed * 7) % (max_val - min_val + 1))),
                lambda: int(min_val + ((seed * 13) % (max_val - min_val + 1))),
                lambda: int(min_val + ((seed * 17) % (max_val - min_val + 1)))
            ]
            
            for approach in approaches:
                try:
                    number = approach()
                    if min_val <= number <= max_val:
                        return number
                except Exception:
                    continue
                    
            return None
        except Exception:
            return None

    def _generate_math_range(self, min_val: int, max_val: int) -> Optional[int]:
        """Generate a number using range-based mathematical operations"""
        try:
            seed = int(time.time() * 1000)
            random.seed(seed)
            
            # Try different range-based approaches
            approaches = [
                lambda: int(min_val + (seed % (max_val - min_val + 1))),
                lambda: int(max_val - (seed % (max_val - min_val + 1))),
                lambda: int(min_val + ((seed * 7) % (max_val - min_val + 1))),
                lambda: int(min_val + ((seed * 13) % (max_val - min_val + 1))),
                lambda: int(min_val + ((seed * 17) % (max_val - min_val + 1)))
            ]
            
            for approach in approaches:
                try:
                    number = approach()
                    if min_val <= number <= max_val:
                        return number
                except Exception:
                    continue
                    
            return None
        except Exception:
            return None

    def _generate_unbounded_random(self, min_val: int, max_val: int) -> Optional[int]:
        """Generate a random number without range constraints"""
        try:
            seed = int(time.time() * 1000)
            random.seed(seed)
            
            # Try different unbounded approaches
            approaches = [
                lambda: int(seed % (max_val - min_val + 1)) + min_val,
                lambda: int((seed * 7) % (max_val - min_val + 1)) + min_val,
                lambda: int((seed * 13) % (max_val - min_val + 1)) + min_val,
                lambda: int((seed * 17) % (max_val - min_val + 1)) + min_val,
                lambda: int((seed * 19) % (max_val - min_val + 1)) + min_val
            ]
            
            for approach in approaches:
                try:
                    number = approach()
                    if min_val <= number <= max_val:
                        return number
                except Exception:
                    continue
                    
            return None
        except Exception:
            return None

    def generate_random_number(self, number_type: str = 'int', min_val: float = -100, max_val: float = 100, 
                             precision: int = 2) -> Union[int, float]:
        """
        Generate a random number that can be either integer or float.
        
        Args:
            number_type (str): Type of number to generate ('int' or 'float')
            min_val (float): Minimum value (inclusive), can be negative
            max_val (float): Maximum value (inclusive), can be negative
            precision (int): Number of decimal places for float (default: 2)
            
        Returns:
            Union[int, float]: Random number of specified type
        """
        # Ensure min_val is less than max_val
        if min_val > max_val:
            min_val, max_val = max_val, min_val
            
        if number_type.lower() == 'int':
            return random.randint(int(min_val), int(max_val))
        elif number_type.lower() == 'float':
            # Generate float with specified precision
            random_float = random.uniform(min_val, max_val)
            return round(random_float, precision)
        else:
            raise ValueError("number_type must be either 'int' or 'float'")

    def generate_unbounded_random(self, number_type: str = 'int', precision: int = 2, 
                                allow_negative: bool = True) -> Union[int, float]:
        """
        Generate a random number without range constraints.
        
        Args:
            number_type (str): Type of number to generate ('int' or 'float')
            precision (int): Number of decimal places for float (default: 2)
            allow_negative (bool): Whether to allow negative numbers (default: True)
            
        Returns:
            Union[int, float]: Random number of specified type
        """
        if number_type.lower() == 'int':
            # Generate a random integer using random.getrandbits
            # This will generate a random integer with up to 32 bits
            number = random.getrandbits(32)
            if allow_negative and random.random() < 0.5:
                number = -number
            return number
        elif number_type.lower() == 'float':
            # Generate a random float between -1 and 1, then scale it
            random_float = random.uniform(-1 if allow_negative else 0, 1)
            return round(random_float, precision)
        else:
            raise ValueError("number_type must be either 'int' or 'float'")

    def generate_math_random(self, function_type: str = 'sine', seed: Optional[int] = None) -> float:
        """
        Generate a random number using mathematical functions.
        
        Args:
            function_type (str): Type of mathematical function to use:
                - 'sine': Uses sine function with random phase
                - 'cosine': Uses cosine function with random phase
                - 'tangent': Uses tangent function with random phase
                - 'exponential': Uses exponential function with random base
                - 'logarithm': Uses natural logarithm with random input
                - 'polynomial': Uses polynomial function with random coefficients
            seed (Optional[int]): Seed for reproducibility (default: None)
            
        Returns:
            float: Random number generated using the specified mathematical function
        """
        if seed is not None:
            random.seed(seed)
            
        # Generate a random phase/input for the function
        x = random.uniform(0, 2 * math.pi)
        
        if function_type.lower() == 'sine':
            # Use sine function with random phase
            return math.sin(x)
            
        elif function_type.lower() == 'cosine':
            # Use cosine function with random phase
            return math.cos(x)
            
        elif function_type.lower() == 'tangent':
            # Use tangent function with random phase
            return math.tan(x)
            
        elif function_type.lower() == 'exponential':
            # Use exponential function with random base
            base = random.uniform(-10, 10)  # Allow negative base
            return math.exp(x * base)
            
        elif function_type.lower() == 'logarithm':
            # Use natural logarithm with random input
            # Ensure input is positive
            input_val = random.uniform(1, 100)
            return math.log(input_val)
            
        elif function_type.lower() == 'polynomial':
            # Use polynomial function with random coefficients
            # Generate random coefficients for a quadratic polynomial
            a = random.uniform(-10, 10)
            b = random.uniform(-10, 10)
            c = random.uniform(-10, 10)
            return a * (x ** 2) + b * x + c
            
        else:
            raise ValueError("function_type must be one of: 'sine', 'cosine', 'tangent', 'exponential', 'logarithm', 'polynomial'")

    def generate_math_sequence(self, function_type: str = 'sine', length: int = 10, seed: Optional[int] = None) -> list[float]:
        """
        Generate a sequence of random numbers using mathematical functions.
        
        Args:
            function_type (str): Type of mathematical function to use (same as generate_math_random)
            length (int): Length of the sequence to generate
            seed (Optional[int]): Seed for reproducibility (default: None)
            
        Returns:
            list[float]: List of random numbers generated using the specified mathematical function
        """
        if seed is not None:
            random.seed(seed)
            
        sequence = []
        for _ in range(length):
            sequence.append(self.generate_math_random(function_type))
        return sequence

    def generate_math_range(self, function_type: str = 'sine', start: float = -1, end: float = 1, 
                          step: float = 0.1, seed: Optional[int] = None) -> list[float]:
        """
        Generate a range of random numbers using mathematical functions.
        
        Args:
            function_type (str): Type of mathematical function to use (same as generate_math_random)
            start (float): Start value of the range (can be negative)
            end (float): End value of the range (can be negative)
            step (float): Step size between values
            seed (Optional[int]): Seed for reproducibility (default: None)
            
        Returns:
            list[float]: List of random numbers generated using the specified mathematical function
        """
        if seed is not None:
            random.seed(seed)
            
        sequence = []
        current = start
        while current <= end:
            sequence.append(self.generate_math_random(function_type))
            current += step
        return sequence

    def generate_shuffled_random(self, 
                               methods: Optional[List[str]] = None,
                               number_type: str = 'int',
                               min_val: float = -100,
                               max_val: float = 100,
                               precision: int = 2,
                               allow_negative: bool = True,
                               seed: Optional[int] = None) -> Union[int, float]:
        """
        Generate a random number using a randomly selected generation method.
        
        Args:
            methods (Optional[List[str]]): List of method names to use for generation.
                If None, uses all available methods.
                Available methods: ['random', 'unbounded', 'math']
            number_type (str): Type of number to generate ('int' or 'float')
            min_val (float): Minimum value for bounded methods (can be negative)
            max_val (float): Maximum value for bounded methods (can be negative)
            precision (int): Number of decimal places for float
            allow_negative (bool): Whether to allow negative numbers for unbounded generation
            seed (Optional[int]): Seed for reproducibility
            
        Returns:
            Union[int, float]: Random number generated using a random method
        """
        if seed is not None:
            random.seed(seed)

        # Define available methods and their parameters
        available_methods = {
            'random': lambda: self.generate_random_number(number_type, min_val, max_val, precision),
            'unbounded': lambda: self.generate_unbounded_random(number_type, precision, allow_negative),
            'math': lambda: self.generate_math_random(random.choice(['sine', 'cosine', 'tangent', 
                                                                    'exponential', 'logarithm', 'polynomial']))
        }

        # If no specific methods are provided, use all available methods
        if methods is None:
            methods = list(available_methods.keys())
        else:
            # Validate provided methods
            invalid_methods = [m for m in methods if m not in available_methods]
            if invalid_methods:
                raise ValueError(f"Invalid methods: {invalid_methods}. Available methods: {list(available_methods.keys())}")

        # Randomly select a method from the provided list
        selected_method = random.choice(methods)
        
        # Generate the random number using the selected method
        return available_methods[selected_method]()

    def generate_shuffled_sequence(self,
                                 length: int = 10,
                                 methods: Optional[List[str]] = None,
                                 number_type: str = 'int',
                                 min_val: float = -100,
                                 max_val: float = 100,
                                 precision: int = 2,
                                 allow_negative: bool = True,
                                 seed: Optional[int] = None) -> List[Union[int, float]]:
        """
        Generate a sequence of random numbers using different generation methods.
        
        Args:
            length (int): Length of the sequence to generate
            methods (Optional[List[str]]): List of method names to use for generation
            number_type (str): Type of number to generate ('int' or 'float')
            min_val (float): Minimum value for bounded methods (can be negative)
            max_val (float): Maximum value for bounded methods (can be negative)
            precision (int): Number of decimal places for float
            allow_negative (bool): Whether to allow negative numbers for unbounded generation
            seed (Optional[int]): Seed for reproducibility
            
        Returns:
            List[Union[int, float]]: List of random numbers generated using different methods
        """
        if seed is not None:
            random.seed(seed)
            
        sequence = []
        for _ in range(length):
            sequence.append(self.generate_shuffled_random(
                methods=methods,
                number_type=number_type,
                min_val=min_val,
                max_val=max_val,
                precision=precision,
                allow_negative=allow_negative
            ))
        return sequence

    def clear_used_numbers(self, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
        """
        Clear used numbers from the database, optionally within a specific range.
        
        Args:
            min_val (Optional[int]): Minimum value of range to clear (inclusive)
            max_val (Optional[int]): Maximum value of range to clear (inclusive)
            
        Returns:
            int: Number of records cleared
        """
        query = self.db.query(models.UsedNumber)
        if min_val is not None:
            query = query.filter(models.UsedNumber.number >= min_val)
        if max_val is not None:
            query = query.filter(models.UsedNumber.number <= max_val)
            
        count = query.count()
        query.delete()
        self.db.commit()
        return count
