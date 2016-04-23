#!/usr/local/bin/python2.7
import argparse
import os

from PIL import Image

thumbnail_size = (4000, 4000)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser('Resize an image')
    argparser.add_argument('filename', type=str)
    argparser.add_argument('-d', type=str, dest='destdir')
    args = argparser.parse_args()
    img = Image.open(args.filename)
    img.thumbnail(thumbnail_size, Image.ANTIALIAS)
    output_filename = "{}_small{}".format(*os.path.splitext(args.filename))
    if args.destdir is not None:
        output_filename = os.path.join(args.destdir, os.path.basename(output_filename))
    with open(output_filename, 'w') as newfile:
        img.save(newfile)
    print "Saved resized image to '{}'".format(output_filename)