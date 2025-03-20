from flask.views import MethodView
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required,
                                get_jwt, get_jwt_identity)
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256

from .db_setup import db
from ..blocklist import BLOCKLIST
from ..models import UserModel
from ..schemas import UserSchema

blp = Blueprint("Users","users",description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
     @blp.arguments(UserSchema)
     @blp.response(201)
     def post(self, user_data):
         user = UserModel(
             username = user_data["username"],
             password=pbkdf2_sha256.hash(user_data["password"])
         )

         db.session.add(user)
         db.session.commit()

         return {"Message":"User created successfully."}



@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data['username']
        ).first()

        if user and pbkdf2_sha256.verify(user_data['password'], user.password):
            access_token = create_access_token(identity=str(user.id), fresh=True)
            refresh_token = create_refresh_token(identity=str(user.id))

            return {"access_token":access_token, "refresh_token":refresh_token}

        abort (401, message = "Invalid credentials! ")



@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token":new_token}

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        try:
            jti = get_jwt()['jti']
            BLOCKLIST.add(jti)
            return {"Message":"User successfully logged out."}
        except TypeError:
            abort(500, message = "Something wrong happened, please try again.")


@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        return UserModel.query.get_or_404(user_id)

    @blp.response(200)
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        db.session.delete(user)
        db.session.commit()

        return {"Message":"User deleted successfully."}