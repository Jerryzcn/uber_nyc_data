# author: Zhongyue Zhang
#################

import fiona
import matplotlib.pyplot as plt
import cPickle as pickle
import pandas as pd
from shapely.geometry import Polygon, MultiPolygon
from matplotlib.colors import Normalize
from matplotlib.collections import PatchCollection
from mpl_toolkits.basemap import Basemap
from descartes import PolygonPatch

EPSG = 3857
extra = 0.01


def main():
    with fiona.open('taxi_zone/taxi_zones_lat_lon.shp', 'r') as shapes:
        lower_left = (shapes.bounds[0] - extra, shapes.bounds[1] - extra)
        upper_right = (shapes.bounds[2] + extra, shapes.bounds[3] + extra)
        width, height = upper_right[0] - lower_left[0], upper_right[1] - lower_left[1]

        m = Basemap(
            projection='merc',
            ellps='WGS84',
            llcrnrlon=lower_left[0],
            llcrnrlat=lower_left[1],
            urcrnrlon=upper_right[0],
            urcrnrlat=upper_right[1],
            lat_ts=0,
            resolution='h',
            suppress_ticks=True)
        m.readshapefile(
            'taxi_zone/taxi_zones_lat_lon',
            'nyc',
            color='none',
            zorder=2)
        #pickup_distribution = pickle.load(open('data/30.p', 'rb'))
        #distribution = pickup_distribution['2015-01-21'][24]  # at noon
        df_map = pd.DataFrame({
            'poly': [Polygon(xy) for xy in m.nyc],
            'zone_id': [zone['LocationID'] for zone in m.nyc_info]})
        df_map['area_m'] = df_map['poly'].map(lambda x: x.area)
        plt.clf()
        fig = plt.figure()
        ax = fig.add_subplot(111, frame_on=False, xticks=[], yticks=[])
        # cmap = plt.get_cmap('Greys_r')
        # df_map['patches'] = df_map['poly'].map(lambda x: PolygonPatch(x, ec='#555555', lw=.2, alpha=1., zorder=4))
        patches = [PolygonPatch(
            x,
            fc='#555555',
            ec='#787878', lw=.25, alpha=.9,
            zorder=4) for x in df_map['poly']]
        pc = PatchCollection(patches, match_original=True)
        # norm = Normalize()
        # pc.set_facecolor(cmap(norm(df_map['jenks_bins'].values)))
        ax.add_collection(pc)
        plt.tight_layout()
        fig.set_size_inches(16.76, 16.88)
        plt.savefig('data/nyc.png', dpi=100, alpha=True)
        plt.show()


if __name__ == '__main__':
    main()
