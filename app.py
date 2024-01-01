import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

from db import db
import models
from models import RevokedTokenModel

from resources.item import blueprint as itemblueprint
from resources.store import blueprint as storeblueprint
from resources.tag import blueprint as tagblueprint
from resources.user import blueprint as userblueprint

def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    migrate = Migrate(app, db)

    api = Api(app)

    api.register_blueprint(itemblueprint)
    api.register_blueprint(storeblueprint)
    api.register_blueprint(tagblueprint)
    api.register_blueprint(userblueprint)

    app.config["JWT_SECRET_KEY"] = "test"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        if RevokedTokenModel.query.filter(RevokedTokenModel.jti == jwt_payload["jti"]).first():
            return True
        return False

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({
                "message": "The token has been revoked",
                "error": "revoked_token"
            }),
            401
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "message": "Token is not fresh",
                    "error": "fresh_token_required"
                }),
                401
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return(
            jsonify({
                "message": "The token has expired.",
                "error": "token_expired"
            }), 401
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return(
            jsonify({
                "message": "Signature verification failed.",
                "error": "invalid_token"
            }), 401
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return(
            jsonify({
                "message": "Request does not contain access token.",
                "error": "missing_token"
            }), 401
        )

    return app
