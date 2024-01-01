from flask import request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt

from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

from db import db


blueprint = Blueprint("items", __name__, description="Operations on items")


@blueprint.route("/item/<int:item_id>")
class Item(MethodView):
    @blueprint.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted"}

    @blueprint.arguments(ItemUpdateSchema)
    @blueprint.response(200, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)

        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item


@blueprint.route("/item")
class ItemList(MethodView):
    @blueprint.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required(fresh=True)
    @blueprint.arguments(ItemSchema)
    @blueprint.response(201, ItemSchema)
    def post(self, item_data):
        jwt = get_jwt()
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, "An error occured while inserting the item")

        return item
