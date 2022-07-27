import datetime
import json
import os
from time import sleep
import cv2
import numpy as np
from easyocr import Reader
from flask import Flask, request
from flask_restful import Api
from json import dumps
from flask import render_template
app = Flask(__name__)
api = Api(app)

#global variable
w = 0
h = 0
global_gird = []
M = 9


@app.route("/", methods=['GET'])
def Welcome():
    return render_template(
        "index.html",
    )


def read_img(image):
    # read image
    image_url = image
    img = cv2.imread(image_url)

    # crop cells
    grid_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # =>gray image
    grid = cv2.bitwise_not(cv2.adaptiveThreshold(
        grid_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 57, 5))  # =>thresh image

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

    #
    finalgrid = []
    for i in range(0, len(tempgrid) - 8, 9):
        finalgrid.append(tempgrid[i:i + 9])
    #
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
            img3 = img3[0:h, 10:w]  # scale follow number
            # read number from image
            num = reader.readtext(img3, allowlist='0123456789')
            if(num == []):
                print(0, end=' ')
                rows.append(0)
            else:
                print(num[0][1], end=' ')
                rows.append(int(num[0][1]))
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
    uri = 'upload/'+image
    read_img(uri)
    sleep(1)
    gird_not_solve = return_cells()
    global global_gird
    global_gird = gird_not_solve
    return json.dumps({"gird_not_solve": gird_not_solve})


@app.route("/solve", methods=['GET'])
def get_solve():
    gird = global_gird.copy()
    if (Sudoku(gird, 0, 0)):
        print_sudoku(gird)
    else:
        print("Can not solve!")
    return json.dumps({"gird": gird})


def print_sudoku(a):
    for i in range(M):
        for j in range(M):
            print(a[i][j], end=" ")
        print()


def solve(grid, row, col, num):
    for x in range(9):
        if grid[row][x] == num:
            return False

    for x in range(9):
        if grid[x][col] == num:
            return False

    startRow = row - row % 3
    startCol = col - col % 3
    for i in range(3):
        for j in range(3):
            if grid[i + startRow][j + startCol] == num:
                return False
    return True


def Sudoku(grid, row, col):
    if (row == M - 1 and col == M):
        return True
    if col == M:
        row += 1
        col = 0
    if grid[row][col] > 0:
        return Sudoku(grid, row, col + 1)
    for num in range(1, M + 1, 1):
        if solve(grid, row, col, num):
            grid[row][col] = num
            if Sudoku(grid, row, col + 1):
                return True
        grid[row][col] = 0
    return False


if __name__ == '__main__':
    app.run(debug=True)
