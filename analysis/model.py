import os, io
from multiprocessing import Pool
try:
    import cPickle as pickle
except:
    import pickle
import numpy as np
import h5py
import pandas as pd
import sklearn.svm as svm
from sklearn.model_selection import GridSearchCV
import sklearn.metrics as sk_metrics
import scipy.stats as stats
import matplotlib.pyplot as plt
from PIL import Image
from skimage.segmentation import find_boundaries

##############
####VISUAL####
##############

def get_pass_mask(d, frame_num=0, img_key='_img'):
    assert img_key in ['_id', '_img', '_depth', '_normal', '_flow'], img_key
    frames = list(d['frames'].keys())
    frames.sort()
    img = d['frames'][frames[frame_num]]['images'][img_key][:]
    img = Image.open(io.BytesIO(img))
    return np.array(img)

def get_segment_map(d):
    return get_pass_mask(d, img_key='_id')

def get_hashed_segment_map(d, val=256):
    segmap = get_segment_map(d) # [H,W,3]
    out = np.zeros(segmap.shape[:2], dtype=np.int32)
    for c in range(segmap.shape[-1]):
        out += segmap[...,c] * (val ** c)
    return out

def get_object_masks(d, exclude_background=True):
    hashed_segmap = get_hashed_segment_map(d)
    obj_ids = list(np.unique(hashed_segmap))
    obj_ids.sort()
    masks = np.array(obj_ids).reshape((1,1,-1)) == hashed_segmap[...,None]
    return masks[...,1:] if exclude_background else masks

def get_full_silhouette(d):
    segmap = get_segment_map(d)
    foreground = segmap.sum(-1) > 0
    return foreground

def silhouette_centroid(foreground):
    H,W = foreground.shape
    him = np.tile(np.linspace(-1.,1.,H)[:,None], [1,W])
    wim = np.tile(np.linspace(-1.,1.,W)[None,:], [H,1])
    hwim = np.stack([him, wim], -1) # [H,W,2]
    return np.sum(hwim * foreground[...,None], axis=(0,1)) / np.sum(foreground)

def silhouette_height(d, normalized=True):
    fg_map = get_full_silhouette(d)
    hinds, _ = np.where(fg_map)
    height = np.abs(hinds.max() - hinds.min()).astype(float)
    if normalized:
        return height / float(fg_map.shape[0])
    else:
        return height

def silhouette_width(d, normalized=True):
    fg_map = get_full_silhouette(d)
    _, winds = np.where(fg_map)
    width =np.abs(winds.max() - winds.min()).astype(float)
    if normalized:
        return width / float(fg_map.shape[1])
    else:
        return width

def silhouette_aspect_ratio(d):
    fg_map = get_full_silhouette(d)
    assert len(fg_map.shape) == 2, fg_map.shape
    hinds, winds = np.where(fg_map)
    if len(hinds) == 0 or len(winds) == 0:
        return np.NaN
    height = np.abs(hinds.max() - hinds.min()).astype(float)
    width = np.abs(winds.max() - winds.min()).astype(float)
    aspect_ratio = (width / height) if height > 0.5 else np.NaN
    return aspect_ratio

def silhouette_area(d):
    fg_map = get_full_silhouette(d)
    return np.mean(fg_map.astype(float))

def silhouette_area_to_bounding_box_area_ratio(d):
    height = silhouette_height(d, normalized=False)
    width = silhouette_width(d, normalized=False)
    bbox_area = (height * width) / np.prod(get_full_silhouette(d).shape).astype(float)
    return silhouette_area(d) / bbox_area

def silhouette_jaggedness(d):
    fg_map = get_full_silhouette(d)
    boundaries = find_boundaries(fg_map, mode='inner', connectivity=2)
    boundary_area = boundaries.astype(float).mean()
    return boundary_area / silhouette_area(d)

def num_visible_objects(d, exclude_background=True):
    hashed_segmap = get_hashed_segment_map(d)
    num_objs = len(np.unique(hashed_segmap))
    return num_objs - 1. if exclude_background else num_objs + 0.

def object_colors(d):
    '''
    return [K,3] array of object RGBs in range [0.,1.]
    '''
    img = get_pass_mask(d, img_key='_img') / 255.
    omasks = get_object_masks(d, exclude_background=True)
    K = omasks.shape[-1]
    obj_colors = np.zeros([K,3], dtype=np.float32)
    for k in range(K):
        ocolor = (img * omasks[...,k:k+1]).sum(axis=(0,1)) # [3]
        ocolor = ocolor / omasks[...,k:k+1].sum(axis=(0,1))
        obj_colors[k] = ocolor

    return obj_colors

def color_diversity(d):
    obj_colors = object_colors(d)
    return np.std(obj_colors, axis=0).mean()

def color_offset(d):
    obj_colors = object_colors(d)
    offsets = np.abs(obj_colors - np.array([0.5,0.5,0.5]).reshape((1,3)))
    return offsets.mean(axis=0).sum()

def get_sorted_block_centroids(d):
    obj_masks = get_object_masks(d)
    K = obj_masks.shape[-1]
    centroids = []
    for k in range(K):
        centroid_k = silhouette_centroid(obj_masks[...,k])
        centroids.append(centroid_k)

    # sort in order of increasing height
    centroids.sort(key=lambda t: -t[0])

    return centroids

def silhouette_centroid_horizontal_offset(d):
    '''
    The absolute deviation between the silhoeutte centroid and
    the bottom block's centroid in the horizontal plane
    '''
    silhouette = get_full_silhouette(d)
    full_centroid = silhouette_centroid(silhouette)
    block_centroids = get_sorted_block_centroids(d)
    return np.abs(full_centroid[1] - block_centroids[0][1])

def pisaness(d):
    '''
    How much a tower looks like the Leaning Tower of Pisa
    That is, the accumulated shift in pixels going from bottom to top
    '''
    centroids = get_sorted_block_centroids(d)

    # accumulated w-shift going up the tower
    return np.abs(centroids[-1][1] - centroids[0][1])


########################
#####INFRASTRUCTURE#####
########################

MODEL_FUNCS = [
    silhouette_height,
    silhouette_width,
    silhouette_aspect_ratio,
    silhouette_area,
    silhouette_area_to_bounding_box_area_ratio,
    silhouette_centroid_horizontal_offset,
    silhouette_jaggedness,
    pisaness,
    num_visible_objects,
    color_offset,
    color_diversity
]

def get_model_funcs():
    return MODEL_FUNCS
