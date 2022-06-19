from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask import jsonify


app = Flask(__name__)
api = Api(app)

class Test(Resource):
    def get(self):
        return "tran anh vu du"

api.add_resource(Test, '/test') # Route_1 


if __name__ == '__main__':
     app.run()