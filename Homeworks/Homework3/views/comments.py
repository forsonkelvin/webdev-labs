from flask import Response, request
from flask_restful import Resource
from . import can_view_post
import json
from models import db, Comment, Post


class CommentListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def post(self):
        body = request.get_json()

        if len(body) < 1:
            return Response(json.dumps({"message": "comment arguments cannot be empty"}), mimetype="application/json", status=400)
        elif body.get('post_id') is None:
            return Response(json.dumps({"message": "post_id is required to make a comment to a post"}), mimetype="application/json", status=400)
        elif body.get('text') is None:
            return Response(json.dumps({"message": "text is required to make a comment to a post"}), mimetype="application/json", status=400)

        user_id = self.current_user.id
        text = body.get('text')
        post_id = body.get('post_id')

        # post_id should be in the list of post_ids of posts by current_user
        posts_by_current_user = Post.query.filter_by(user_id=self.current_user.id)
        posts_by_current_user_ids = [post.id for post in posts_by_current_user]

        if not isinstance(post_id, int):
            return Response(json.dumps({"message": "post_id is not an integer"}), mimetype="application/json", status=400)
        elif not Post.query.get(post_id):
            return Response(json.dumps({"message": "post_id is not valid a post id"}), mimetype="application/json", status=404)

        elif post_id not in posts_by_current_user_ids:
            return Response(json.dumps({"message": "post_id is unrelated to current user"}), mimetype="application/json", status=404)

        # create comment
        comment = Comment(text, user_id, post_id)
        db.session.add(comment)
        db.session.commit()
        return Response(json.dumps(comment.to_dict()), mimetype="application/json", status=201)


class CommentDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def delete(self, id):
        if not id.isnumeric():
            return Response(json.dumps({'message': 'Invalid post id'}), mimetype="application/json", status=400)

        # a user can only delete their own comment:
        comment = Comment.query.get(id)
        if not comment or comment.user_id!= self.current_user.id:
            return Response(json.dumps({'message': 'Comment does not exist'}), mimetype="application/json", status=404)


        Comment.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'Comment {0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        CommentListEndpoint,
        '/api/comments',
        '/api/comments/',
        resource_class_kwargs={'current_user': api.app.current_user}

    )
    api.add_resource(
        CommentDetailEndpoint,
        '/api/comments/<id>',
        '/api/comments/<id>',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
