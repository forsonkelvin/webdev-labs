from operator import and_
from flask import Response, request
from flask_restful import Resource
from models import Following, db
from . import can_view_post, get_authorized_user_ids
import json


def get_path():
    return request.host_url + 'api/following'


class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user

    def get(self):
        following_ids = Following.query.filter_by(user_id=self.current_user.id)

        following = [following.to_dict_following() for following in following_ids]
        return Response(json.dumps(following), mimetype="application/json", status=200)

    def post(self):
        body = request.get_json()

        if len(body) < 1:
            return Response(json.dumps({"message": "missing 1 positional argument"}), mimetype="application/json",
                            status=400)
        elif body.get('user_id') is None:
            return Response(json.dumps({"message": "user_id is required to make a post"}),
                            mimetype="application/json", status=400)

        following_id = body.get('user_id')
        if not isinstance(following_id, int):
            return Response(json.dumps({"message": "user_id is not of valid type"}),
                            mimetype="application/json", status=400)
        
        elif not Following.query.get(following_id):
            return Response(json.dumps({"message": "following_id is not valid"}),
                        mimetype="application/json", status=404)

        try:
            following = Following(self.current_user.id, following_id)
            db.session.add(following)
            db.session.commit()
            return Response(json.dumps(following.to_dict_following()), mimetype="application/json", status=201)
        except:
            return Response(json.dumps({"message": "user_id is not valid"}), mimetype="application/json", status=400)

        

class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user

    def delete(self, id):

        if not id.isnumeric():
            return Response(json.dumps({"message": "user_id is not of valid type"}),
                    mimetype="application/json", status=400)
        
        following = Following.query.get(id)

        if not following or following.user_id != self.current_user.id:
            return Response(json.dumps({"message" : "cannot delete following not created by user"}), mimetype="application/json", status=404)
        
        Following.query.filter_by(id=id).delete()
        db.session.commit()
        serialized_data = {
            'message': 'Post {0} successfully deleted.'.format(id)
        }
        return Response(json.dumps(serialized_data), mimetype="application/json", status=200)
            


def initialize_routes(api):
    api.add_resource(
        FollowingListEndpoint,
        '/api/following',
        '/api/following/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        FollowingDetailEndpoint,
        '/api/following/<id>',
        '/api/following/<id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
