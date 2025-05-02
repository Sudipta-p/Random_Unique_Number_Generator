# Unique Random Number Server

A FastAPI-based HTTP server that generates unique random numbers. Each number is guaranteed to be unique across all requests, even after server restarts.

## Features

- RESTful endpoint `/random` that returns unique random numbers
- Persistent storage using SQLite
- Numbers are never repeated, even after server restarts
- Automatic range expansion when numbers are exhausted
- Automatic database clearing for exhausted ranges
- Multiple mathematical approaches for number generation
- Built with FastAPI for high performance and automatic API documentation
- Comprehensive unit tests

## Installation

1. Clone Repo & Set Up Environment:
```bash
git clone https://github.com/Sudipta-p/Random_Unique_Number_Generator.git
cd Random_Unique_Number_Generator
python -m venv myenv
source myenv/bin/activate  # or myenv\Scripts\activate (Windows)
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the server with:
```bash
uvicorn app.main:app --reload
```

The server will be available at http://localhost:8000

- API endpoint: http://localhost:8000/random
- API documentation: http://localhost:8000/docs

## Running Tests

```bash
pytest
```

## Design Considerations

### Range Management
- Default range: -1,000,000 to 1,000,000
- Automatic range expansion when exhausted
- Automatic database clearing for exhausted ranges
- Multiple expansion attempts before full reset

### Number Generation
- Multiple mathematical approaches for generating numbers
- Automatic method shuffling for better distribution
- Support for both positive and negative numbers
- Efficient uniqueness checking

### Scalability
- Uses SQLite for persistence (can be easily swapped with PostgreSQL for higher scale)
- Implements efficient number generation and tracking
- Handles concurrent requests safely
- Automatic database maintenance

### Future Improvements
1. Switch to PostgreSQL for higher concurrency
2. Implement number range partitioning for distributed systems
3. Add caching layer for frequently accessed ranges
4. Implement batch number pre-generation for better performance
5. Add monitoring for range exhaustion patterns

## API Response Format

```json
{
    "number": 42
}
```

## Error Handling

The API will return appropriate HTTP status codes:
- 200: Successfully generated a unique number
- 503: Service temporarily unavailable (when all ranges are exhausted and being reset) 
