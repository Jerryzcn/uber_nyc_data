import StringIO
import os
import urllib
from math import log, exp, tan, atan, pi, ceil

import fiona
from PIL import Image

import download_google_map

# Algorithm from
# http://stackoverflow.com/questions/7490491/capture-embedded-google-map-image-with-python-without-using-a-browser
EARTH_RADIUS = 6378137
EQUATOR_CIRCUMFERENCE = 2 * pi * EARTH_RADIUS
INITIAL_RESOLUTION = EQUATOR_CIRCUMFERENCE / 256.0
ORIGIN_SHIFT = EQUATOR_CIRCUMFERENCE / 2.0


def latlontopixels(lat, lon, zoom):
    mx = (lon * ORIGIN_SHIFT) / 180.0
    my = log(tan((90 + lat) * pi / 360.0)) / (pi / 180.0)
    my = (my * ORIGIN_SHIFT) / 180.0
    res = INITIAL_RESOLUTION / (2 ** zoom)
    px = (mx + ORIGIN_SHIFT) / res
    py = (my + ORIGIN_SHIFT) / res
    return px, py


def pixelstolatlon(px, py, zoom):
    res = INITIAL_RESOLUTION / (2 ** zoom)
    mx = px * res - ORIGIN_SHIFT
    my = py * res - ORIGIN_SHIFT
    lat = (my / ORIGIN_SHIFT) * 180.0
    lat = 180 / pi * (2 * atan(exp(lat * pi / 180.0)) - pi / 2.0)
    lon = (mx / ORIGIN_SHIFT) * 180.0
    return lat, lon


def download_map(ullat, ullon, lrlat, lrlon, maptype):
    ############################################

    zoom = 14  # be careful not to get too many images!

    # Set some important parameters
    scale = 1
    maxsize = 640

    # convert all these coordinates to pixels
    ulx, uly = latlontopixels(ullat, ullon, zoom)
    lrx, lry = latlontopixels(lrlat, lrlon, zoom)

    # calculate total pixel dimensions of final image
    dx, dy = lrx - ulx, uly - lry

    # calculate rows and columns
    cols, rows = int(ceil(dx / maxsize)), int(ceil(dy / maxsize))

    # calculate pixel dimensions of each small image
    bottom = 120
    largura = int(ceil(dx / cols))
    altura = int(ceil(dy / rows))
    alturaplus = altura + bottom

    final = Image.new("RGB", (int(dx), int(dy)))
    for x in range(cols):
        for y in range(rows):
            dxn = largura * (0.5 + x)
            dyn = altura * (0.5 + y)
            latn, lonn = pixelstolatlon(ulx + dxn, uly - dyn - bottom / 2, zoom)
            position = ','.join((str(latn), str(lonn)))
            urlparams = urllib.urlencode({'center': position,
                                          'zoom': str(zoom),
                                          'size': '%dx%d' % (largura, alturaplus),
                                          'maptype': maptype,
                                          'sensor': 'false',
                                          'scale': scale})
            url = 'http://maps.google.com/maps/api/staticmap?' + urlparams
            f = urllib.urlopen(url)
            im = Image.open(StringIO.StringIO(f.read()))
            final.paste(im, (int(x * largura), int(y * altura)))
    return final


def download_map_image(filename, maptype, bounds, zoom, size, scale):
    extra = 0.01
    if os.path.isfile(filename):
        print 'already downloaded %s' % filename
        return
    image = download_google_map.download_map(bounds[3] + extra, bounds[0] - extra, bounds[1] - extra, bounds[2] + extra,
                                             maptype)
    image.save(filename)


'''
def download_map_image(filename, maptype, center, zoom, size, scale):
    if os.path.isfile(filename):
        print 'already downloaded %s' % filename
        return
    urlparams = urllib.urlencode({'center': ','.join((str(center[0]), str(center[1]))),
                                  'zoom': str(zoom),
                                  'size': '%dx%d' % (size[0], size[1]),
                                  'maptype': maptype,
                                  'sensor': 'false',
                                  'scale': scale})
    im_buf = StringIO.StringIO(urllib.urlopen('http://maps.google.com/maps/api/staticmap?' + urlparams).read())
    image = Image.open(im_buf)
    image.save(filename)
'''



def main():
    with fiona.open('taxi_zone/taxi_zones_lat_lon.shp', 'r') as shapes:
        download_map_image('map_img/satellite.png', 'satellite', shapes.bounds, 10, (1000, 1325), 2)
        download_map_image('map_img/roadmap.png', 'roadmap', shapes.bounds, 10, (1000, 1325), 2)
        download_map_image('map_img/terrain.png', 'terrain', shapes.bounds, 10, (1000, 1325), 2)
        download_map_image('map_img/hybrid.png', 'hybrid', shapes.bounds, 10, (1000, 1325), 2)


if __name__ == '__main__':
    main()
