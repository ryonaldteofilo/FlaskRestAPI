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
    @jwt_required()
    @blueprint.response(200, ItemSchema)
    def get(self, item_id):
        """Finding an item

        Return an item based on ID.
        """
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required(fresh=True)
    def delete(self, item_id):
        """Removing an item

        Remove an item based on ID.
        """
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted successfully."}

    @jwt_required(fresh=True)
    @blueprint.arguments(ItemUpdateSchema)
    @blueprint.response(200, ItemSchema)
    def put(self, item_data, item_id):
        """Updating an item

        Update an item based on ID.
        """
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
    @jwt_required()
    @blueprint.response(200, ItemSchema(many=True))
    def get(self):
        """Getting all items

        Return all items.
        """
        return ItemModel.query.all()

    @jwt_required(fresh=True)
    @blueprint.arguments(ItemSchema, description="Details of item to insert")
    @blueprint.response(201, ItemSchema)
    def post(self, item_data):
        """Adding an item

        Adding an item by providing its details.
        """
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting the item.")
        return item
