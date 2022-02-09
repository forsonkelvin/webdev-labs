from flask import Response, request
from flask_restful import Resource
from models import Following, User
from . import get_authorized_user_ids, get_suggested_user_ids
import json

class SuggestionsListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def get(self):

        suggested_ids_set = list(get_suggested_user_ids(self.current_user))

        max_suggested = len(suggested_ids_set)
        if max_suggested > 7:
            max_suggested = 7

        suggestedUsers = [User.query.get(suggested_ids_set[i]).to_dict() for i in range(max_suggested)]

        return Response(json.dumps(suggestedUsers), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        SuggestionsListEndpoint,
        '/api/suggestions',
        '/api/suggestions/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
