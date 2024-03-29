from flask import request
from flask.views import MethodView

from flask_jwt_extended import jwt_required

from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models import TagModel, StoreModel, ItemModel
from schemas import TagSchema, TagAndItemSchema

from db import db


blueprint = Blueprint("tags",
                      __name__,
                      description="""Operations on tags.
                      A tag belongs to a store and can be linked to multiple items in that store.
                      """)


@blueprint.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @jwt_required()
    @blueprint.response(200, TagSchema)
    def get(self, tag_id):
        """Finding a tag

        Returns a tag based on ID.
        """
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @jwt_required(fresh=True)
    @blueprint.response(
        200,
        example={"message": "Tag deleted."}
    )
    @blueprint.alt_response(
        404,
        description="Tag not found"
    )
    @blueprint.alt_response(
        400,
        description="""Returned if the tag is assigned
        to one or more items. In this case, the tag is not deleted"""
    )
    def delete(self, tag_id):
        """Removing a tag

        Remove a tag based on ID.
        """
        tag = TagModel.query.get_or_404(tag_id)
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}
        abort(
            400,
            message="""Could not delete tag.
            Make sure tag is not associated with any items, then try again.
            """
        )


@blueprint.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    @jwt_required(fresh=True)
    @blueprint.response(201, TagSchema)
    def post(self, item_id, tag_id):
        """Link a item to a tag

        Link an item to a tag based on ID. Item and tag should belong to the same store.
        """
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if item.store.id != tag.store.id:
            abort(400, message="""Ensure item and tag belong to the same
            store before linking.""")

        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")
        return tag

    @jwt_required(fresh=True)
    @blueprint.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        """Removing a link between an item and a tag

        Remove a link between item and tag based on ID.
        """
        item = ItemModel.query.get_or_404(item_id)
        tag = ItemModel.query.get_or_404(tag_id)

        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")
        return {"message": "Item removed from tag", "item": item, "tag": tag}


@blueprint.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @jwt_required()
    @blueprint.response(200, TagSchema(many=True))
    def get(self, store_id):
        """Getting all tags of a store

        Return all tags from a store based on ID.
        """
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @jwt_required(fresh=True)
    @blueprint.arguments(TagSchema)
    @blueprint.response(201, TagSchema)
    def post(self, tag_data, store_id):
        """Adding a tag to a store

        Adding a tag to a store by providing its details.
        """
        if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first():
            abort(400, message="A tag with that name already exists in that store.")

        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return tag
