# Lunch-log

A Django application for logging and analyzing lunch receipts, with personalized restaurant recommendations.

## Project Description

Lunch-log is a web application that allows users to:

- Log their lunch receipts, including restaurant information, date, and cost
- Track their lunch spending over time
- Get personalized restaurant recommendations based on their history and preferences

The application uses Django and Django REST Framework for the backend, with PostgreSQL for data storage, Celery for background tasks, and MinIO for object storage. It also integrates with the Google Places API to fetch restaurant details.

## Features

- User authentication with email and password
- Receipt management (upload, view, edit, delete)
- Restaurant recommendations based on user history and preferences
- Background tasks for data processing
- Object storage for receipt images

## Technology Stack

- **Backend**: Django 5.2, Django REST Framework
- **Database**: PostgreSQL 14
- **Object Storage**: MinIO
- **Background Tasks**: Celery with Redis
- **Containerization**: Docker, Docker Compose
- **Dependency Management**: Poetry
- **External APIs**: Google Places API

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Make (optional, for convenience commands)
- Git

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Django
DJANGO_SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1
ENVIRONMENT=development

# Database
DJANGO_DATABASE_NAME=postgres
DJANGO_DATABASE_USER=postgres
DJANGO_DATABASE_PASSWORD=postgres
DJANGO_DATABASE_HOST=db
DJANGO_DATABASE_PORT=5432

# MinIO
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=lunch-log

# Celery
CELERY_BROKER_URL=redis://redis:6379/0

# Google Places API
GOOGLE_API_KEY=your_google_api_key
GOOGLE_PLACES_TEXT_SEARCH_URL=https://maps.googleapis.com/maps/api/place/findplacefromtext/json
GOOGLE_PLACES_DETAILS_URL=https://maps.googleapis.com/maps/api/place/details/json
```

Replace `your_secret_key` with a secure random string and `your_google_api_key` with your Google Places API key.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/lunch-log.git
   cd lunch-log
   ```

2. Create the `.env` file as described above.

3. Build and start the Docker containers:
   ```bash
   make start-build
   ```

   Alternatively, if you don't have Make:
   ```bash
   docker compose up --build
   ```
4. The application will be available at http://localhost:8000

## API Documentation

### Authentication Endpoints

#### Sign Up
- **URL**: `/api/auth/signup/`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "full_name": "John Doe",
    "password": "securepassword",
    "dietary_restrictions": "vegetarian"
  }
  ```
  
  Note: The `dietary_restrictions` field is optional.
- **Response**: 201 Created
  ```json
  {
    "message": "Signup successful"
  }
  ```

#### Login
- **URL**: `/api/auth/login/`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response**: 200 OK
  ```json
  {
    "message": "Login successful"
  }
  ```

#### CSRF Token
- **URL**: `/api/auth/csrf/`
- **Method**: GET
- **Response**: 200 OK
  ```json
  {
    "message": "CSRF cookie set"
  }
  ```

### Receipt Endpoints

#### Create Receipt
- **URL**: `/api/receipts/`
- **Method**: POST
- **Request Body** (multipart/form-data):
  ```
  image: [file]
  date: "2023-07-15"
  price: "15.99"
  restaurant_name: "NENI Berlin"
  address: "Friedrichstraße 185-190, 10117 Berlin, Germany"
  ```
- **Response**: 201 Created

#### List Receipts
- **URL**: `/api/receipts/`
- **Method**: GET
- **Query Parameters**:
  - `month`: Filter by month (format: YYYY-MM)
- **Response**: 200 OK
  ```json
  [
    {
      "id": 1,
      "image": "http://localhost:8000/media/receipts/user_1/receipt.jpg",
      "date": "2023-07-15",
      "price": "15.99",
      "restaurant_name": "NENI Berlin",
      "address": "Friedrichstraße 185-190, 10117 Berlin, Germany"
    }
  ]
  ```
  
#### Get Receipt
- **URL**: `/api/receipts/{id}/`
- **Method**: GET
- **Response**: 200 OK
  ```json
  {
    "id": 1,
    "image": "http://localhost:8000/media/receipts/user_1/receipt.jpg",
    "date": "2023-07-15",
    "price": "15.99",
    "restaurant_name": "NENI Berlin",
    "address": "Friedrichstraße 185-190, 10117 Berlin, Germany"
  }
  ```

#### Update Receipt
- **URL**: `/api/receipts/{id}/`
- **Method**: PUT/PATCH
- **Request Body**:
  ```json
  {
    "date": "2023-07-16",
    "price": "16.99"
  }
  ```
- **Response**: 200 OK

#### Delete Receipt
- **URL**: `/api/receipts/{id}/`
- **Method**: DELETE
- **Response**: 204 No Content

### Restaurant Recommendation Endpoints

#### Get Recommendations
- **URL**: `/api/recommendations/?city=Berlin`
- **Method**: GET
- **Query Parameters**:
  - `city`: The city to get recommendations for (required)
- **Response**: 200 OK
  ```json
  [
    {
      "id": 1,
      "place_id": "ChIJ-RAVYVVQqEcRIfxE6EjRZ38",
      "name": "NENI Berlin",
      "address": "Budapester Str. 40, 10787 Berlin, Germany",
      "city": "Berlin",
      "cuisine": [
            "restaurant",
            "food",
            "point_of_interest",
            "establishment"
        ],
      "rating": 4.3,
      "user_ratings_total": 4306,
      "phone_number": "030 120221201"
    }
  ]
  ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.