from turtle import pos
from flask import Response, request
from flask_restful import Resource
from models import Bookmark, db
import json
from . import can_view_post

class BookmarksListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def get(self):

        current_user_bookmarks = [bookmark.to_dict() for bookmark in Bookmark.query.filter_by(user_id=self.current_user.id)]

        return Response(json.dumps(current_user_bookmarks), mimetype="application/json", status=200)

    def post(self):
        body = request.get_json()

        if len(body) < 1:
            return Response(json.dumps({"message": "bookmark arguments cannot be empty"}), mimetype="application/json",
                            status=400)
        elif body.get('post_id') is None:
            return Response(json.dumps({"message": "post_id is required to make a post"}),
                            mimetype="application/json", status=400)

        post_id = body.get('post_id')
        user_id = self.current_user.id

        if not isinstance(post_id, int):
            return Response(json.dumps({"message": "post_id is not of valid type"}),
                            mimetype="application/json", status=400)
        
        if not can_view_post(post_id, self.current_user):
            return Response(json.dumps({"message" : "User does not have permission to bookmark post"}), mimetype="application/json", status=404)
        # create bookmark:
        
        try:
            bookmark = Bookmark(user_id, post_id)
            db.session.add(bookmark)
            db.session.commit()
            return Response(json.dumps(bookmark.to_dict()), mimetype="application/json", status=201)
        except:
            return Response(json.dumps({"message": "bookmark already exists"}), mimetype="application/json", status=400)
        

class BookmarkDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def delete(self, id):
        if not id.isnumeric():
            return Response(json.dumps({"message": "bookmark id is not of valid type"}),
                    mimetype="application/json", status=400)
        
        bookmark = Bookmark.query.get(id)

        if not bookmark or bookmark.user_id != self.current_user.id:
            return Response(json.dumps({"message" : "cannot delete bookmark not created by user"}), mimetype="application/json", status=404)
        
        bookmark.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'bookmark {0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        BookmarksListEndpoint,
        '/api/bookmarks',
        '/api/bookmarks/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        BookmarkDetailEndpoint,
        '/api/bookmarks/<id>',
        '/api/bookmarks/<id>',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
