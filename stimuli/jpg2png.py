#!/usr/bin/env python
# coding: utf-8

import numpy as np
import os, sys
import pandas as pd
from PIL import Image
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--in_dir', type=str, default='coolTower')
    parser.add_argument('--out_dir', type=str, default='pngTower')
    parser.add_argument('--scale', type=int, default=0.25)    
    args = parser.parse_args()

    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)
    fnames = os.listdir(args.in_dir)
    for i,fname in enumerate(fnames):
        im = Image.open(os.path.join(args.in_dir,fname))
        new_width = int(im.size[0]*args.scale)
        new_height = int(im.size[1]*args.scale)
        im = im.resize((new_width,new_height),Image.ANTIALIAS) ## resize         
        im.save(os.path.join(args.out_dir,'{}.png'.format(fname.split('.')[0])))
        print('Converting {}'.format(fname))
    print('Done!')