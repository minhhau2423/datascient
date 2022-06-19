from email.mime import image
from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask import jsonify
import cv2
import os

app = Flask(__name__)
api = Api(app)

@app.route("/")
def Welcome():
    return "<h1>Welcome to digital image processing API</h1>"

class Test(Resource):
    def get(self):
        absolute_path = os.path.join(os.getcwd(), 'datascient', 'Image', 'img.jpg')
        return absolute_path


api.add_resource(Test, '/test') 


if __name__ == '__main__':
    absolute_path = os.path.join(os.getcwd(), 'datascient', 'Image', 'img.jpg')
   
    img = cv2.imread(absolute_path,1)
    cv2.imshow(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    path = 'E:\_TRUONGMINHHAU\DataScience\Demo_DIP\datascient\Image'
    cv2.imwrite(os.path.join(path , 'waka.jpg'), gray)
    cv2.waitKey(0)
    app.run()