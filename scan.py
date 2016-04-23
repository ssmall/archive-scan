#!/usr/local/bin/python2.7
import argparse
import os
import sys

from PIL import Image
import pyocr
import pyocr.builders


def extract_text(filename, output_filename):
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)
    # The tools are returned in the recommended order of usage
    tool = tools[0]
    print("Will use tool '%s'" % (tool.get_name()))

    langs = tool.get_available_languages()
    print("Available languages: %s" % ", ".join(langs))
    lang = langs[0]
    print("Will use lang '%s'" % (lang))

    txt = tool.image_to_string(
        Image.open(filename),
        lang=lang,
        builder=pyocr.builders.TextBuilder()
    )


    with open(output_filename, 'w') as txtfile:
        txtfile.write(txt.encode("UTF-8"))

    print "Text contents saved as '{}'".format(output_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Archive a scan of an album page")
    parser.add_argument('filename', type=str)
    parser.add_argument('-d', type=str, dest='destdir')
    args = parser.parse_args()
    output_filename = "{}.txt".format(os.path.splitext(args.filename)[0])
    if args.destdir is not None:
        output_filename = os.path.join(args.destdir, os.path.basename(output_filename))
    extract_text(args.filename, output_filename)
