import datetime
import json
import os
from random import random
from time import sleep
import cv2
import numpy as np
from easyocr import Reader
from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps

app = Flask(__name__)
api = Api(app)
# a function to read the
w = 0
h = 0


@app.route("/", methods=['GET'])
def Welcome():
    return 'sudoku api'


def read_img(image):
    # I wanted the user to have the liberty to choose the image
    #print("Enter image name: ")
    image_url = image
    # image url also conatins the image extension eg. .jpg or .png
    # reading in greayscale
    img = cv2.imread(image_url)
    gray = cv2.imread(image_url, cv2.IMREAD_GRAYSCALE)

    # Note that kernel sizes must be positive and odd and the kernel must be square.
    proc = cv2.GaussianBlur(img.copy(), (9, 9), 0)
    process = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 57, 5)
    process = cv2.bitwise_not(process, process)

   # here grid is the cropped image
    grid_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # VERY IMPORTANT
    # Adaptive thresholding the cropped grid and inverting it
    grid = cv2.bitwise_not(cv2.adaptiveThreshold(
        grid_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 57, 5))
    # grid = grid_gray

    # cv2.imshow('d', grid)
    # cv2.waitKey()
    edge_h = np.shape(grid)[0]
    edge_w = np.shape(grid)[1]
    celledge_h = edge_h // 9
    celledge_w = np.shape(grid)[1] // 9
    global w, h
    w = celledge_w
    h = celledge_h
    tempgrid = []

    for i in range(celledge_h, edge_h + 1, celledge_h):
        for j in range(celledge_w, edge_w + 1, celledge_w):
            rows = grid[i - celledge_h:i]
            tempgrid.append([rows[k][j - celledge_w:j]
                            for k in range(len(rows))])

        # Creating the 9X9 grid of images
    finalgrid = []
    for i in range(0, len(tempgrid) - 8, 9):
        finalgrid.append(tempgrid[i:i + 9])
    # Converting all the cell images to np.array
    for i in range(9):
        for j in range(9):
            finalgrid[i][j] = np.array(finalgrid[i][j])
    try:
        for i in range(9):
            for j in range(9):
                os.remove("BoardCells/cell" + str(i) + str(j) + ".jpg")
    except:
        pass
    for i in range(9):
        for j in range(9):
            cv2.imwrite(str("BoardCells/cell" + str(i) +
                        str(j) + ".jpg"), finalgrid[i][j])


def return_cells():
    rows = []
    all = []
    reader = Reader(['en'])
    k = 0
    for i in range(9):
        for j in range(9):
            img = cv2.imread(str("BoardCells/cell" + str(i) +
                                 str(j) + ".jpg"))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 2))
            img2 = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
            img3 = cv2.blur(img2, (3, 3))
            img3 = img3[0:h, 10:w]
            # cv2.imshow('cc', img3)
            # cv2.waitKey(50)
            num = reader.readtext(img3, allowlist='0123456789')
            if(num == []):
                print(0, end=' ')
                rows.append(0)
            else:
                print(num[0][1], end=' ')
                rows.append(num[0][1])
            k = k+1
            if(k == 9):
                all.append(rows)
                rows = []
                print()
                k = 0
    return all


@app.route('/upload', methods=['POST'])
def upload():
    x = datetime.datetime.now()
    dateTimeStr = str(x).replace('-', '').replace(':',
                                                  '').replace(' ', '').replace('.', '')
    file = request.files['file']
    filename = dateTimeStr+'_'+file.filename
    file.save(os.path.join('upload/'+filename))
    return filename


@app.route("/get_all_cells", methods=['GET'])
def get_cells():
    image = request.args.get('image')
    read_img(image)
    sleep(1)
    return json.dumps(return_cells())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
