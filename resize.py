#!/usr/local/bin/python2.7
import argparse
import os

from PIL import Image

thumbnail_size = (4000, 4000)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser('Resize an image')
    argparser.add_argument('filename', type=str)
    args = argparser.parse_args()
    img = Image.open(args.filename)
    img.thumbnail(thumbnail_size, Image.ANTIALIAS)
    with open("{}_small{}".format(*os.path.splitext(args.filename)), 'w') as newfile:
        img.save(newfile)
