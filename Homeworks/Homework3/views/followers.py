from flask import Response, request
from flask_restful import Resource
from models import Following
from . import can_view_post, get_authorized_user_ids
import json

def get_path():
    return request.host_url + 'api/posts/'

class FollowerListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user

    def get(self):
        followers_ids = Following.query.filter_by(following_id=self.current_user.id)

        followers = [following.to_dict_follower() for following in followers_ids]
        return Response(json.dumps(followers), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        FollowerListEndpoint,
        '/api/followers',
        '/api/followers/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
