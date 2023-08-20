from flasgger import swag_from
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.models import Bookmark, db
from src.constants.http_status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)
import validators


bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")


@bookmarks.route("/", methods=["GET", "POST"])
@jwt_required()
def create_get_bookmarks():
    current_user_id = get_jwt_identity()
    if request.method == "POST":
        body = request.get_json().get("body", "")
        url = request.get_json().get("url", "")
        if not validators.url(url):
            return {"error": "Invalid URL"}, HTTP_400_BAD_REQUEST
        if Bookmark.query.filter_by(url=url).first() is not None:
            return {"error": "Bookmark already exists"}, HTTP_409_CONFLICT

        bookmark = Bookmark(body=body, url=url, user_id=current_user_id)
        db.session.add(bookmark)
        db.session.commit()
        return (
            jsonify(
                {
                    "id": bookmark.id,
                    "body": bookmark.body,
                    "url": bookmark.url,
                    "short_url": bookmark.short_url,
                    "visits": bookmark.visits,
                    "created_at": bookmark.created_at,
                    "updated_at": bookmark.updated_at,
                }
            ),
            HTTP_201_CREATED,
        )
    else:
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=10, type=int)
        bookmarks = Bookmark.query.filter_by(user_id=current_user_id).paginate(
            page=page, per_page=per_page
        )
        print(type(bookmarks))

        data = []
        for bookmark in bookmarks:
            data.append(
                {
                    "id": bookmark.id,
                    "body": bookmark.body,
                    "url": bookmark.url,
                    "short_url": bookmark.short_url,
                    "visits": bookmark.visits,
                    "created_at": bookmark.created_at,
                    "updated_at": bookmark.updated_at,
                }
            )

        print(data)

        return (
            jsonify(
                {
                    "data": data,
                    "meta": {
                        "page": bookmarks.page,
                        "pages": bookmarks.pages,
                        "total": bookmarks.total,
                        "prev_page": bookmarks.prev_num,
                        "next_page": bookmarks.next_num,
                        "has_next": bookmarks.has_next,
                        "has_prev": bookmarks.has_prev,
                    },
                }
            ),
            HTTP_200_OK,
        )


@bookmarks.get("/<int:bookmark_id>")
@jwt_required()
def get_bookmark(bookmark_id):
    current_user_id = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=current_user_id).first()
    if bookmark is None:
        return jsonify({"message": "Bookmark not found"}), HTTP_404_NOT_FOUND

    return (
        jsonify(
            {
                "id": bookmark.id,
                "body": bookmark.body,
                "url": bookmark.url,
                "short_url": bookmark.short_url,
                "visits": bookmark.visits,
                "created_at": bookmark.created_at,
                "updated_at": bookmark.updated_at,
            }
        ),
        HTTP_200_OK,
    )


@bookmarks.route("/<int:bookmark_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_bookmark(bookmark_id):
    current_user_id = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=current_user_id).first()
    if bookmark is None:
        return jsonify({"message": "Bookmark not found"}), HTTP_404_NOT_FOUND

    body = request.get_json().get("body", "")
    url = request.get_json().get("url", "")
    if not validators.url(url):
        return {"error": "Invalid URL"}, HTTP_400_BAD_REQUEST

    bookmark.body = body
    bookmark.url = url

    db.session.commit()

    return (
        jsonify(
            {
                "id": bookmark.id,
                "body": bookmark.body,
                "url": bookmark.url,
                "short_url": bookmark.short_url,
                "visits": bookmark.visits,
                "created_at": bookmark.created_at,
                "updated_at": bookmark.updated_at,
            }
        ),
        HTTP_200_OK,
    )


@bookmarks.delete("/<int:bookmark_id>")
@jwt_required()
def delete_bookmark(bookmark_id):
    current_user_id = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=current_user_id).first()
    if bookmark is None:
        return jsonify({"message": "Bookmark not found"}), HTTP_404_NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()

    return (
        jsonify({}),
        HTTP_204_NO_CONTENT,
    )


@bookmarks.get("/stats")
@jwt_required()
@swag_from("./docs/bookmarks/stats.yml")
def get_bookmark_stats():
    current_user_id = get_jwt_identity()

    data = []

    items = Bookmark.query.filter_by(user_id=current_user_id).all()
    for item in items:
        new_link = {
            "visits": item.visits,
            "url": item.url,
            "id": item.id,
            "short_url": item.short_url,
        }

        data.append(new_link)

    return (
        jsonify(
            {
                "data": data,
            }
        ),
        HTTP_200_OK,
    )
