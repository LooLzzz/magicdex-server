from flask import jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

class JwtApi(Resource):
    @jwt_required()
    def get(self):
        user_id, username = get_jwt_identity()
        return jsonify(msg='success', username=username)
