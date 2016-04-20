#!/usr/local/bin/python2.7
import argparse
import os
import sys

from PIL import Image
import pyocr
import pyocr.builders


def extract_text(filename):
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

    txtfilename = "{}.txt".format(os.path.splitext(filename)[0])
    with open(txtfilename, 'w') as txtfile:
        txtfile.write(txt.encode("UTF-8"))

    print "Text contents saved as '{}'".format(txtfilename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Archive a scan of an album page")
    parser.add_argument('filename', type=str)
    args = parser.parse_args()
    extract_text(args.filename)
