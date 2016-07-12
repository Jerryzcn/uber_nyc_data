# author: Zhongyue Zhang
#################

import StringIO
import urllib

import fiona
from PIL import Image


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
    with fiona.open('taxi_zone/taxizones_lat_lon.shp', 'r') as shapes:

        download_map_image()


if __name__ == '__main__':
    main()
