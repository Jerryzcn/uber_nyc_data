# author: Zhongyue Zhang
#################

from PIL import Image
import urllib, StringIO
import numpy as np
import shapefile
import os


def download_map_image(filename, center, zoom, size, scale):
    urlparams = urllib.urlencode({'center': center,
                                  'zoom': str(zoom),
                                  'size': '%dx%d' % (size[0], size[1]),
                                  'maptype': 'satellite',
                                  'sensor': 'false',
                                  'scale': scale})
    im_buf = StringIO(urllib.urlopen('http://maps.google.com/maps/api/staticmap?' + urlparams).read())
    image = Image.open(im_buf)
    image.save(filename)


def main():
    download_map_image()


if __name__ == '__main__':
    main()

