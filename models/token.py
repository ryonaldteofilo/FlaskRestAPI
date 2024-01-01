from db import db


class RevokedTokenModel(db.Model):
    __tablename__ = "revoked_token"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String, unique=True, nullable=False)
