from flask import Response, request
from flask_restful import Resource
from models import Post, User, db
from . import can_view_post, get_authorized_user_ids
import json
from sqlalchemy import *


def get_path():
    return request.host_url + 'api/posts/'


def get_params():
    return request.args


class PostListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def get(self):
        # TODO:
        # 1. No security implemented;
        # 2. limit is hard coded (versus coming from the query parameter)
        # 3. No error checking

        default_limit = 10
        max_limit = 50
        params = get_params()

        query_limit = params['limit'] if 'limit' in params else None

        if query_limit:
            if not query_limit.isnumeric():
                return Response(json.dumps({"message": "Limit parameter is not a number"}), mimetype="application/json",
                                status=400)

            query_limit = int(query_limit)
            if query_limit > max_limit:
                return Response(json.dumps({"message": "Limit parameter exceeds maximum limit"}),
                                mimetype="application/json", status=400)
        else:
            query_limit = default_limit

        following_ids = get_authorized_user_ids(self.current_user)
        following_posts = Post.query.filter(Post.user_id.in_(following_ids)).order_by(Post.pub_date.desc()).limit(
            query_limit)
        results = [following_post.to_dict() for following_post in following_posts.all()]

        return Response(json.dumps(results), mimetype="application/json", status=200)

    def post(self):
        body = request.get_json()

        if len(body) < 1:
            return Response(json.dumps({"message": "post arguments cannot be empty"}), mimetype="application/json",
                            status=400)
        elif body.get('image_url') is None:
            return Response(json.dumps({"message": "image_url is required to make a post"}),
                            mimetype="application/json", status=400)

        image_url = body.get('image_url')
        caption = body.get('caption')
        alt_text = body.get('alt_text')
        user_id = self.current_user.id  # id of the user who is logged in

        # create post:
        post = Post(image_url, user_id, caption, alt_text)
        db.session.add(post)
        db.session.commit()
        return Response(json.dumps(post.to_dict()), mimetype="application/json", status=201)


class PostDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def patch(self, id):

        if not id.isnumeric():
            return Response(json.dumps({'message': 'Invalid post id'}), mimetype="application/json", status=400)

        post = Post.query.get(id)

        # a user can only edit their own post:
        if not post or post.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)

        body = request.get_json()
        post.image_url = body.get('image_url') or post.image_url
        post.caption = body.get('caption') or post.caption
        post.alt_text = body.get('alt_text') or post.alt_text

        # commit changes:
        db.session.commit()
        return Response(json.dumps(post.to_dict()), mimetype="application/json", status=200)

    def delete(self, id):

        if not id.isnumeric():
            return Response(json.dumps({'message': 'Invalid post id'}), mimetype="application/json", status=400)

        # a user can only delete their own post:
        post = Post.query.get(id)
        if not post or post.user_id != self.current_user.id:
            return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)

        Post.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'Post {0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)

    def get(self, id):

        if not id.isnumeric():
            return Response(json.dumps({'message': 'Invalid post id'}), mimetype="application/json", status=400)

        post = Post.query.get(id)

        # if the user is not allowed to see the post or if the post does not exist, return 404:
        if not post or not can_view_post(post.id, self.current_user):
            return Response(json.dumps({'message': 'Post does not exist'}), mimetype="application/json", status=404)

        return Response(json.dumps(post.to_dict()), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        PostListEndpoint,
        '/api/posts', '/api/posts/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        PostDetailEndpoint,
        '/api/posts/<id>', '/api/posts/<id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
