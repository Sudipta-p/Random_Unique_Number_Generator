# Unique Random Number Server

A FastAPI-based HTTP server that generates unique random numbers. Each number is guaranteed to be unique across all requests, even after server restarts.

## Features

- RESTful endpoint `/random` that returns unique random numbers
- Persistent storage using SQLite
- Numbers are never repeated, even after server restarts
- Built with FastAPI for high performance and automatic API documentation
- Includes unit tests

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
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

### Scalability
- Uses SQLite for persistence (can be easily swapped with PostgreSQL for higher scale)
- Implements efficient number generation and tracking
- Handles concurrent requests safely

### Future Improvements
1. Switch to PostgreSQL for higher concurrency
2. Implement number range partitioning for distributed systems
3. Add caching layer for frequently accessed ranges
4. Implement batch number pre-generation for better performance

## API Response Format

```json
{
    "number": 42
}
``` 