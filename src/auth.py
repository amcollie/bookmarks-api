from flasgger import swag_from
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from werkzeug.security import check_password_hash, generate_password_hash
from src.constants.http_status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_409_CONFLICT,
)
from src.models import db, User
import jwt
import validators

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post("/register")
@swag_from("./docs/auth/register.yml")
def register():
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    if len(password) < 6:
        return jsonify({"message": "password too short"}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({"message": "username too short"}), HTTP_400_BAD_REQUEST

    if not username.isalnum():
        return (
            jsonify({"message": "username must be alphanumeric"}),
            HTTP_400_BAD_REQUEST,
        )

    if not validators.email(email):
        return jsonify({"message": "invalid credentials"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"message": "email taken"}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"message": "username taken"}), HTTP_409_CONFLICT

    password_hash = generate_password_hash(password)

    user = User(username=username, email=email, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "user created",
                "user": {"username": user.username, "email": user.email},
            }
        ),
        HTTP_201_CREATED,
    )


@auth.post("/login")
@swag_from("./docs/auth/login.yml")
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if not validators.email(email):
        return jsonify({"message": "invalid credentials"}), HTTP_400_BAD_REQUEST

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"message": "invalid credentials"}), HTTP_401_UNAUTHORIZED
    if not check_password_hash(user.password_hash, password):
        return jsonify({"message": "invalid credentials"}), HTTP_401_UNAUTHORIZED

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return (
        jsonify(
            {
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            }
        ),
        HTTP_200_OK,
    )


@auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({"username": user.username, "email": user.email}), HTTP_200_OK


@auth.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)

    return jsonify({"access_token": access_token}), HTTP_200_OK
