import fiona
from fiona.crs import from_epsg
from pyproj import Proj, transform

OUTPUT_EPSG = 4326
OUTPUT_EPSG_STR = 'epsg:4326'


def convert(original_crs, destination_crs, coord):
    return transform(original_crs, destination_crs, coord[0], coord[1])


def main():
    with fiona.open('taxi_zone/taxi_zones.shp', 'r') as shapes:
        with fiona.open('taxi_zone/taxi_zones_lat_lon.shp', 'w', 'ESRI Shapefile', shapes.schema.copy(),
                        crs=from_epsg(OUTPUT_EPSG)) as new_shapes:
            original_crs = Proj(shapes.crs)
            destination_crs = Proj(init=OUTPUT_EPSG_STR)
            counter = 0
            for zone in shapes:
                for i in xrange(len(zone['geometry']['coordinates'])):
                    for j in xrange(len(zone['geometry']['coordinates'][i])):
                        if zone['geometry']['type'] == 'MultiPolygon':
                            for k in xrange(len(zone['geometry']['coordinates'][i][j])):
                                zone['geometry']['coordinates'][i][j][k] = \
                                    convert(original_crs, destination_crs,
                                            zone['geometry']['coordinates'][i][j][k])
                        else:
                            zone['geometry']['coordinates'][i][j] = \
                                convert(original_crs, destination_crs,
                                        zone['geometry']['coordinates'][i][j])
                new_shapes.write(zone)
                counter += 1
    print('Done. Converted %d zones' % counter)


if __name__ == '__main__':
    main()
