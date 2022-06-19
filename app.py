from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask import jsonify



app = Flask(__name__)
api = Api(app)

class Test(Resource):
    def get(self):
        return "TEST response"

@app.route("/", methods=["GET"])
def Welcome():
    return "<h1>Welcome to digital image processing API</h1>"


api.add_resource(Test, '/test') 


if __name__ == '__main__':
     app.run()