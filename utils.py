import cv2
import numpy as np
import glob
import os
import json
import tqdm
from functools import cmp_to_key
import re
import copy

def is_title(text):
    if text.lower() in ["by"]: return True
    if len(re.split(r"(:)", text)) > 1: return True
    return False

def is_horizontal_overlap(
    key_loc, field_loc, val_max=10000000, offset=None, right_side=True, thres=0.0
):

    """
    Description: determinating if 2 locations is horizontal overlapped (key .vs field)
    - Input:
        + key_loc: tuple list of 4-corner coordinates for key location
        + field_loc: tuple list of 4-corner coordinates for field location
        + val_max: maximal vertical location in searching
    """

    # key location
    x0, y0 = key_loc[0]
    x1, y1 = key_loc[2]

    if offset is not None:
        h = y1 - y0
        y1 += offset(h)
        y0 += offset(h)

    x0, y0 = int(x0), int(y0)
    x1, y1 = int(x1), int(y1)

    # field location
    x, y = field_loc[0]
    x_, y_ = field_loc[2]
    x, y = int(x), int(y)
    x_, y_ = int(x_), int(y_)

    # get y max
    y_max = int(max(y_, y1))
    Y = np.zeros((y_max, 2))
    Y[y0:y1, 0] = 1
    Y[y:y_, 1] = 1
    Y = Y.prod(axis=-1)

    # is horizontal
    isHorizontal = False
    if right_side:
        if (x > x0) and (x < val_max):  # field is on the right side of considered key
            isHorizontal = (
                Y.sum() / min(y1 - y0, y_ - y) > thres
            )  # max(y1-y0, y_-y)>thres

    else:
        isHorizontal = Y.sum() / min(y1 - y0, y_ - y) > thres  # max(y1-y0, y_-y) >thres

    return isHorizontal

def is_vertical_overlap(
    key_loc, field_loc, val_max=10000000, offset=None, down_side=True, thres=0.0
):

    """
    Description: determinating if 2 locations is vertical overlapped (key .vs field)
    - Input:
        + key_loc: tuple list of 4-corner coordinates for key location
        + field_loc: tuple list of 4-corner coordinates for field location
        + val_max: maximal vertical location in searching
    """

    # key location
    x0, y0 = key_loc[0]
    x1, y1 = key_loc[2]

    if offset is not None:
        h = x1 - x0
        x1 += offset(h)
        x0 += offset(h)

    x0, y0 = int(x0), int(y0)
    x1, y1 = int(x1), int(y1)

    # field location
    x, y = field_loc[0]
    x_, y_ = field_loc[2]
    x, y = int(x), int(y)
    x_, y_ = int(x_), int(y_)

    # get x max
    x_max = int(max(x_, x1))
    X = np.zeros((x_max, 2))
    X[x0:x1, 0] = 1
    X[x:x_, 1] = 1
    X = X.prod(axis=-1)

    # is horizontal
    isVertical = False
    if down_side:
        if (y > y0) and (y < val_max):  # field is on the right side of considered key
            isVertical = (
                X.sum() / min(x1 - x0, x_ - x) > thres
            )  # max(y1-y0, y_-y)>thres

    else:
        isVertical = X.sum() / min(x1 - x0, x_ - x) > thres  # max(y1-y0, y_-y) >thres

    return isVertical

def compare_location(textline1, textline2):
    (x1, y1), _, _, _ = textline1["location"]
    (x2, y2), _, _, _ = textline2["location"]
    if is_horizontal_overlap(
        textline1["location"], textline2["location"], right_side=False, thres=0.4
    ):
        return x1 - x2
    else:
        return y1 - y2

def sort_textline(text_list):
    return sorted(text_list, key=cmp_to_key(compare_location))


def sort_layout_output(layout_ouput):
    # sorting textline
    layout_ouput = sort_textline(layout_ouput)
    # adding line and cell info
    idx = 0
    sub_idx = 0
    for i, item in enumerate(layout_ouput):
        if i > 0:
            if is_horizontal_overlap(
                item["location"], layout_ouput[i-1]["location"], right_side=False, thres=0.4
            ):
                sub_idx += 1
                item.update({
                    "line": idx,
                    "cell": sub_idx,
                    #"text": f"line {idx}.{sub_idx}: " + item.get('text'),
                })
            else:
                idx +=1
                sub_idx = 0
                item.update({
                    "line": idx,
                    "cell": sub_idx,
                    #"text": f"line {idx}.{sub_idx}: " + item.get('text'),
                })
        else:
            item.update({
                "line": idx,
                "cell": sub_idx,
                #"text": f"line {idx}.{sub_idx}: " + item.get('text'),
            })

    return layout_ouput