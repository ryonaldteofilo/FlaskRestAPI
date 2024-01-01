from db import db


class TagItemModel(db.Model):
    __tablename__ = "tags_items"

    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"))
    items_id = db.Column(db.Integer, db.ForeignKey("items.id"))
