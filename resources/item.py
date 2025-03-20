from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt

from .db_setup import db
from ..models import ItemModel
from ..schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint("items", __name__, description="Operations on items")

@blp.route("/items/<int:item_id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        return ItemModel.query.get_or_404(item_id)

    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort (401, message = "Admin privileges required.")
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()

        return {"message": "Item deleted."}

    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data['price']
            item.name = item_data['name']
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item

@blp.route("/items")
class ItemsList(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort (500, message="An error occured while inserting an item")

        return item