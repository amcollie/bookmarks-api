from flasgger import Swagger, swag_from
from flask import Flask, jsonify, redirect
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv, find_dotenv
from os import getenv, path
from src.auth import auth
from src.bookmarks import bookmarks
from src.constants.http_status_codes import (
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from src.models import db, Bookmark
from src.config.swagger import template, swagger_config

load_dotenv(find_dotenv())


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    database_path = path.join(app.instance_path, getenv("SQLALCHEMY_DB_URI"))

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=getenv("SECRET_KEY", "no-one-will-guess-this"),
            SQLALCHEMY_DATABASE_URI=f"sqlite:///{database_path}",
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=getenv("SECRET_KEY", "no-one-will-guess-this"),
            SWAGGER={
                "title": "Bookmarks API",
                "uiversion": 3,
                "version": "1.0.0",
                "schemes": ["http", "https"],
                "consumes": ["application/json"],
            },
        )
    else:
        app.config.from_mapping(test_config)

    JWTManager(app)
    db.app = app
    db.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    @app.get("/<short_url>")
    @swag_from("./docs/short_url.yml")
    def redirect_to_short_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()
        bookmark.visits += 1
        db.session.commit()
        return redirect(bookmark.url)

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def page_not_found(e):
        return jsonify({"error": "Not found"}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def internal_server_error(e):
        return (
            jsonify({"error": "Internal server error"}),
            HTTP_500_INTERNAL_SERVER_ERROR,
        )

    Swagger(app, template=template, config=swagger_config)

    return app
