from flask import request
from flask.views import MethodView
from passlib.hash import pbkdf2_sha256

from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_jwt_extended import(
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)

from schemas import UserSchema
from models import UserModel, RevokedTokenModel

from db import db


blueprint = Blueprint("users", __name__, description="Operations on users")


@blueprint.route("/register")
class UserRegister(MethodView):
    @blueprint.arguments(UserSchema)
    def post(self, user_data):
        """Registering a user

        Register a user by providing credentials.
        """
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists.")

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"])
        )
        db.session.add(user)
        db.session.commit()
        return {"message": "User created successfully."}


@blueprint.route("/login")
class UserLogin(MethodView):
    @blueprint.arguments(UserSchema)
    def post(self, user_data):
        """Getting user token

        Get user token by providing credentials.
        """
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            accessToken = create_access_token(identity=user.id, fresh=True)
            refreshToken = create_refresh_token(identity=user.id)
            return {"access_token": accessToken, "refresh_token": refreshToken}
        abort(401, message="Invalid credentials.")


@blueprint.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        """Revoking user token

        Revoke a user token.
        """
        jti = str(get_jwt()["jti"])
        revoked = RevokedTokenModel(jti=jti)
        db.session.add(revoked)
        db.session.commit()
        return {"message": "Token revoked successfully."}


@blueprint.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        """Refreshing user token

        Get a new user token by providing a refresh token.
        """
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}


@blueprint.route("/user/<int:user_id>")
class UserRegister(MethodView):
    @jwt_required()
    @blueprint.response(200, UserSchema)
    def get(self, user_id):
        """Finding a user

        Return a user based on ID.
        """
        user = UserModel.query.get_or_404(user_id)
        return user

    @jwt_required(fresh=True)
    def delete(self, user_id):
        """Removing a user

        Remove a user based on ID.
        """
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200
