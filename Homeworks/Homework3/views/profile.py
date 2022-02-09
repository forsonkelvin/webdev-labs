from flask import Response, request
from flask_restful import Resource
from models import Post, User, db
import json

def get_path():
    return request.host_url + 'api/posts/'

class ProfileDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def get(self):

        profile = User.query.get(self.current_user.id)
        
        return Response(json.dumps(profile.to_dict()), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        ProfileDetailEndpoint,
        '/api/profile',
        '/api/profile/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
