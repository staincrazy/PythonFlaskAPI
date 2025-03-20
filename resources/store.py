from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from .db_setup import db
from ..models import StoreModel
from ..schemas import StoreSchema

blp = Blueprint("stores",__name__, description="Operations on stores")

@blp.route("/stores/<int:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        return StoreModel.query.get_or_404(store_id)

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()

        return {"message":"Store deleted."}

    @blp.response(200, StoreSchema)
    def put(self, store_id):
        StoreModel.query.get_or_404(store_id)
        raise NotImplementedError("Updating a store is not implemented")

@blp.route("/stores")
class StoresList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, messgae = "A store with such name already exists")
        except SQLAlchemyError:
            abort (500, messgae = "An error occurred while adding a store")

        return store