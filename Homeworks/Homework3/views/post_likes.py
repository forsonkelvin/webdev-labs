from flask import Response
from flask_restful import Resource
from models import LikePost, Post, db
import json
from . import can_view_post

class PostLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def post(self, post_id):

        if not post_id.isnumeric():
            return Response(json.dumps({"message": "Invalid Post ID type"}), mimetype="application/json", status=400)

        post_id = int(post_id)
        post = Post.query.get(post_id)
        
        # Check if post exist for specified post_id
        if not post:
            return Response(json.dumps({"message" : "Post does not exist"}), mimetype="application/json", status=404)
        
        # Check to see if user has permission to like specified post
        if not can_view_post(post_id, self.current_user):
            return Response(json.dumps({"message" : "User does not have permission to view post"}), mimetype="application/json", status=404)

        
        # Try committing a like if not then is a duplicate
        try:
            like = LikePost(self.current_user.id, post_id)
            db.session.add(like)
            db.session.commit()
        except:
            return Response(json.dumps({"message" : "Cannot duplicate like for post"}), mimetype="application/json", status=400)
        return Response(json.dumps(like.to_dict()), mimetype="application/json", status=201)

class PostLikesDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def delete(self, post_id, id):
        
        if not id.isnumeric():
            return Response(json.dumps({"message": "user_id is not of valid type"}),
                    mimetype="application/json", status=400)
        
        likePost = LikePost.query.get(id)

        if not likePost or likePost.user_id != self.current_user.id:
            return Response(json.dumps({"message" : "cannot delete like not created by user"}), mimetype="application/json", status=404)
        
        likePost.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'like {0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)



def initialize_routes(api):
    api.add_resource(
        PostLikesListEndpoint,
        '/api/posts/<post_id>/likes',
        '/api/posts/<post_id>/likes/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        PostLikesDetailEndpoint,
        '/api/posts/<post_id>/likes/<id>',
        '/api/posts/<post_id>/likes/<id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
