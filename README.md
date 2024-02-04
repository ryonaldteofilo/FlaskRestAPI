# FlaskRestAPI
A simple RESTful API written with Python, Flask and its extensions.

## Features
- JWT integration with Flask-JWT-Extended.
- Interaction with PostgreSQL database with SQLAlchemy and psycopg2.
- Database migrations with Flask-migrate and alembic.
- OpenAPI documentation with Swagger UI.

## Running it locally
### Docker
docker run -dp 5000:5000 -w /app -v "%cd%:/app" flaskrestapi
docker build -t "flaskrestapi" .
