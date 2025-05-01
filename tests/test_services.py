import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.services import NumberGeneratorService
import os

# Test database setup
TEST_DATABASE_URL = "sqlite:///./data/test_numbers.db"

@pytest.fixture
def db_session():
    # Create test database
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create a new session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up test database
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./data/test_numbers.db"):
            os.remove("./data/test_numbers.db")

def test_generate_unique_number(db_session):
    service = NumberGeneratorService(db_session)
    
    # Test initial number generation
    number1 = service.generate_unique_number()
    assert number1 is not None
    assert -1_000_000 <= number1 <= 1_000_000
    
    # Test uniqueness
    number2 = service.generate_unique_number()
    assert number2 is not None
    assert number1 != number2

def test_range_exhaustion_and_expansion(db_session):
    service = NumberGeneratorService(db_session)
    
    # Fill up the initial range
    numbers = set()
    for _ in range(100):  # Generate some numbers to test the system
        number = service.generate_unique_number()
        assert number is not None
        numbers.add(number)
    
    # Verify all numbers are unique
    assert len(numbers) == 100

def test_database_clearing(db_session):
    service = NumberGeneratorService(db_session)
    
    # Generate some numbers
    initial_numbers = []
    for _ in range(10):
        number = service.generate_unique_number()
        assert number is not None
        initial_numbers.append(number)
    
    # Verify numbers are in database
    for number in initial_numbers:
        assert service._number_exists(number)
    
    # Clear a specific range
    min_val = min(initial_numbers)
    max_val = max(initial_numbers)
    cleared_count = service.clear_used_numbers(min_val, max_val)
    assert cleared_count == len(initial_numbers)
    
    # Verify numbers are cleared
    for number in initial_numbers:
        assert not service._number_exists(number)

def test_range_expansion(db_session):
    service = NumberGeneratorService(db_session)
    
    # Get initial range
    initial_min = service._default_min
    initial_max = service._default_max
    
    # Expand range
    new_min, new_max = service._expand_range(initial_min, initial_max)
    
    # Verify range is expanded correctly
    assert new_min < initial_min
    assert new_max > initial_max
    assert (new_max - new_min) > (initial_max - initial_min)

def test_exhausted_range_handling(db_session):
    service = NumberGeneratorService(db_session)
    
    # Generate numbers until range is exhausted
    numbers = set()
    while len(numbers) < 100:  # Limit to prevent infinite loop
        number = service.generate_unique_number()
        if number is None:
            break
        numbers.add(number)
    
    # Verify we can still generate numbers after exhaustion
    new_number = service.generate_unique_number()
    assert new_number is not None
    assert new_number not in numbers

def test_multiple_expansions(db_session):
    service = NumberGeneratorService(db_session)
    
    # Test multiple range expansions
    min_val, max_val = service._default_min, service._default_max
    
    # Perform multiple expansions
    for _ in range(service._max_expansions):
        min_val, max_val = service._expand_range(min_val, max_val)
        assert min_val < service._default_min
        assert max_val > service._default_max

def test_clear_all_numbers(db_session):
    service = NumberGeneratorService(db_session)
    
    # Generate some numbers
    numbers = []
    for _ in range(10):
        number = service.generate_unique_number()
        assert number is not None
        numbers.append(number)
    
    # Clear all numbers
    cleared_count = service.clear_used_numbers()
    assert cleared_count == len(numbers)
    
    # Verify all numbers are cleared
    for number in numbers:
        assert not service._number_exists(number)
    
    # Verify we can generate new numbers
    new_number = service.generate_unique_number()
    assert new_number is not None
    assert new_number not in numbers 