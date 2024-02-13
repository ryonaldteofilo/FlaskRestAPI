# FlaskRestAPI
A simple RESTful API written with Python, Flask and its extensions.

## Features
- JWT integration with Flask-JWT-Extended.
- Interaction with PostgreSQL database with SQLAlchemy and psycopg2.
- Database migrations with Flask-migrate and alembic.
- OpenAPI documentation with Swagger UI.

## Demo
- A demo service is currently deployed on `https://flask-rest-api-demo.onrender.com`.
- Swagger UI documentation available at `https://flask-rest-api-demo.onrender.com/swagger-ui`.

## Running it locally
### Flask/Gunicorn
- During development, the flask app can be ran by running the database migrations first through `flask db upgrade` and running the flask app in development mode with `flask run`. For Linux systems, you can use a WSGI server such as `gunicorn`.

### Docker
A docker image can be built with
`docker build -t "flaskrestapi"` and ran with
`docker run -dp 5000:5000 -w /app -v "%cd%:/app" flaskrestapi` with it accessible via `http://127.0.0.1:5000`.