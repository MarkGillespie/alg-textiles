#!/usr/local/bin/python3

import numpy as np
import argparse
import imutils
import statistics
import cv2
import math

base_size = 500
match_threshold = 0.7

def print_pattern(pattern):
    print('w=' + str(len(pattern)))
    for y in range(len(pattern[0])):
        pattern_row = ""
        for x in range(len(pattern)):
            pattern_row += pattern[x][y]
        print(pattern_row)

def extract_pattern_from_grid(image, show_img=False):
    resized = imutils.resize(image, width=base_size)
    gray    = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0);
    thresh  = cv2.threshold(blurred, 170, 255, cv2.THRESH_BINARY)[1]

    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)

    widths = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if 0.95 < w/h and w/h < 1.05 and w > 5:
            widths.append(w)
            cv2.drawContours(thresh, [c], 0, (0, 255, 0), 3)
    if len(widths) == 0:
        raise Exception('no squares found')

    grid_width = statistics.median(widths) + 2

    int_grid_width = 32

    thresh = imutils.resize(image, width=int(base_size * int_grid_width / grid_width))
    thresh = cv2.addWeighted(thresh, 2.5, thresh, 0, -100)
    thresh = cv2.GaussianBlur(thresh, (3, 3), 0);
    thresh = cv2.addWeighted(thresh, 1.6, thresh, 0, -100)
    grid_width = int_grid_width
    inner_grid_width = grid_width - 3

    h, w, d = thresh.shape
    pattern_width  = int(w / grid_width)
    pattern_height = int(h / grid_width)

    pattern_grid = [[" " for y in range(pattern_height)] for x in range(pattern_width)]

    yo = cv2.imread('patterns/lace_chart_images/yarn_over.png')
    yo = imutils.resize(yo, width=inner_grid_width)
    dr = cv2.imread('patterns/lace_chart_images/dec_right.png')
    dr = imutils.resize(dr, width=inner_grid_width)
    dl = cv2.imread('patterns/lace_chart_images/dec_left.png')
    dl = imutils.resize(dl, width=inner_grid_width)
    pl = cv2.imread('patterns/lace_chart_images/purl.png')
    pl = imutils.resize(pl, width=(inner_grid_width-6))

    res = cv2.matchTemplate(thresh, yo, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res > match_threshold)
    for pt in zip(*loc[::-1]):
        x = int(pt[0] / grid_width)
        y = int(pt[1] / grid_width)
        pattern_grid[x][y] = "o"
        cv2.rectangle(thresh, pt, (pt[0] + inner_grid_width, pt[1] + inner_grid_width), (0, 0, 255), 2)
        
    res = cv2.matchTemplate(thresh, dr, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res > match_threshold)
    for pt in zip(*loc[::-1]):
        x = int(pt[0] / grid_width)
        y = int(pt[1] / grid_width)
        pattern_grid[x][y] = "/"
        cv2.rectangle(thresh, pt, (pt[0] + inner_grid_width, pt[1] + inner_grid_width), (0, 255, 0), 2)

    res = cv2.matchTemplate(thresh, dl, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res > match_threshold)
    for pt in zip(*loc[::-1]):
        x = int(pt[0] / grid_width)
        y = int(pt[1] / grid_width)
        pattern_grid[x][y] = "\\"
        cv2.rectangle(thresh, pt, (pt[0] + inner_grid_width, pt[1] + inner_grid_width), (255, 0, 0), 2)

    res = cv2.matchTemplate(thresh, pl, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res > match_threshold)
    for pt in zip(*loc[::-1]):
        x = int(pt[0] / grid_width)
        y = int(pt[1] / grid_width)
        pattern_grid[x][y] = "."
        cv2.rectangle(thresh, pt, (pt[0] + inner_grid_width, pt[1] + inner_grid_width), (255, 0, 255), 2)

    if show_img:
        cv2.imshow("image", thresh)
        cv2.waitKey(0)
    return pattern_grid

def find_pattern_grid(image, show_img=False):
    image = cv2.copyMakeBorder(image, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    # image = imutils.resize(image, width=800)
    gray    = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((3, 3), np.uint8)
    gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    # blurred = cv2.GaussianBlur(gray, (9, 9), 0);
    thresh = gray
    thresh = cv2.addWeighted(thresh, 2, thresh, 0, -40)
    thresh  = cv2.threshold(thresh, 150, 255, cv2.THRESH_BINARY)[1]
    color_thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)

    contours = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE);
    contours = imutils.grab_contours(contours)

    largest_contour = None
    second_largest_contour = None
    largest_area = -1
    second_largest_area = -1
    for c in contours:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * perimeter, True)
        n_sides = len(approx)
        if n_sides == 4:
            # cv2.drawContours(color_thresh, [c], 0, (0, 255, 0), 3)
            area = cv2.contourArea(c, False)
            if area > largest_area:
                second_largest_area    = largest_area
                second_largest_contour = largest_contour

                largest_area = area
                largest_contour = c 
            elif area > second_largest_area:
                second_largest_area    = area
                second_largest_contour = c

    cv2.drawContours(color_thresh, [second_largest_contour], 0, (0, 255, 0), 3)
    rect = cv2.minAreaRect(second_largest_contour)
    box  = cv2.boxPoints(rect)
    box  = np.int0(box)
    cv2.drawContours(color_thresh, [box], 0, (0, 0, 255), 2)

    angle = rect[2]

    if abs(angle) < 45:
        width  = int(rect[1][0])
        height = int(rect[1][1])

        src_points = box.astype("float32")
        dst_points = np.array([
                               [0, height-1],
                               [0, 0],
                               [width-1, 0],
                               [width-1, height-1]
                               ], dtype="float32")
    else:
        width  = int(rect[1][1])
        height = int(rect[1][0])

        src_points = box.astype("float32")
        dst_points = np.array([
                               [width-1, height-1],
                               [0, height-1],
                               [0, 0],
                               [width-1, 0]
                               ], dtype="float32")
    M = cv2.getPerspectiveTransform(src_points, dst_points)
    warped = cv2.warpPerspective(image, M, (width, height))

    if show_img:
        cv2.imshow("image", warped)
        cv2.waitKey(0)

    return warped

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help="path to the image file")
args = vars(ap.parse_args())

image = cv2.imread(args["image"])
pattern_grid = find_pattern_grid(image)
pattern = extract_pattern_from_grid(pattern_grid)
print_pattern(pattern)

