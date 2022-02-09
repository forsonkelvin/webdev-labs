from flask import Response
from flask_restful import Resource
from models import Following, Story
from . import get_authorized_user_ids
import json

class StoriesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def get(self):

        auth_users_ids = get_authorized_user_ids(self.current_user)
        stories = Story.query.filter(Story.user_id.in_(auth_users_ids))

        Stories_lst = [story.to_dict() for story in stories]
        return Response(json.dumps(Stories_lst), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        StoriesListEndpoint,
        '/api/stories',
        '/api/stories/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )