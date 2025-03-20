from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from .db_setup import db
from ..models import TagModel, StoreModel, ItemModel
from ..schemas import TagSchema, TagAndItemSchema

blp = Blueprint("Tags","tags", "Operations on tags")

@blp.route("/stores/<int:store_id>/tag")
class TagInStore(MethodView):
    @blp.response(200,TagSchema(many=True))
    def get(self, store_id):
        return StoreModel.query.get_or_404(store_id).tags.all()


    @blp.arguments(TagSchema)
    @blp.response(201,TagSchema)
    def post(self, tag_data,store_id):
        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort (
                500,
                message=f"An error occurred while saving a tag! {str(e)}"
            )

        return tag


@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        return TagModel.query.get_or_404(tag_id)

    @blp.response(
        202,
        description="Deletes a tag if no item is tagged with it",
    )
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"Message":"Tag deleted"}



@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort (500, message="An error occurred while adding a tag")

        return tag

    @blp.response(200,TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting a tag")

        return {"Message":"Item removed from tag", "item":item, "tag":tag}


