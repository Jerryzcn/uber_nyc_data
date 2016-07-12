# author: Zhongyue Zhang
#################

import fiona
from PIL import Image


def main():
    with fiona.open('taxi_zone/taxi_zones_lat_lon.shp', 'r') as shapes:
        # TODO


if __name__ == '__main__':
    main()
