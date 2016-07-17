# author: Zhongyue Zhang
#################
from __future__ import division

import numpy as np
import matplotlib.pyplot as plt
import cPickle as pickle
import pandas as pd
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Polygon
from matplotlib.colors import Normalize
from matplotlib.collections import PatchCollection

from descartes import PolygonPatch
from PIL import Image, ImageTk
import os
import Tkinter as tk


EPSG = 3857
extra = 0.01

NUM_THREADS = 4

lower_left = (-74.26559136315211, 40.48611539517036)
upper_right = (-73.6900090639354, 40.925532777002594)

LOCATIONID_MAP = dict({
    (57, 56),
    (104, 103),
    (105, 103),
})


def main():
    m = Basemap(
        projection='merc',
        ellps='WGS84',
        llcrnrlon=lower_left[0],
        llcrnrlat=lower_left[1],
        urcrnrlon=upper_right[0],
        urcrnrlat=upper_right[1],
        lat_ts=0,
        resolution='i')
    m.readshapefile(
        'taxi_zone/taxi_zones_lat_lon',
        'nyc',
        color='none',
        zorder=2)
    pickups = pickle.load(open('data/30_unnormalized.p', 'rb'))
    gen_heat_map(m, pickups)
    
    print 'finished'

class Uber_figure(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        #img2_image = Image.open(os.path.join('uber_nyc_data-master','img2.png'))
        #img2_image = Image.open('img2.png')
        
        date = '2015-05-02'
        time = 24
        img2_image = Image.open('data2/heat_map/nyc-' + str(date) + '-' + str(time) + '.png')
        img2_image = img2_image.resize((512, 512), Image.ANTIALIAS)
        img2 = ImageTk.PhotoImage(img2_image)
        
        self.l1 = tk.Label(self, image=img2)
        self.l1.image = img2
        #self.l1 = tk.Label(self, image=ImageTk.PhotoImage(image))
        self.l2 = tk.Label(self, text="", width=40)
        self.l1.pack(side = "bottom", fill = "both", expand = "yes")
        self.l2.pack(side="top", fill="y")
        
        self.l1.bind("<Enter>", self.on_enter)
        self.l1.bind("<Leave>", self.on_leave)
        
    def on_enter(self, event):
        self.l2.configure(text="This is the uber nyc image")

    def on_leave(self, enter):
        self.l2.configure(text="")

def gen_heat_map(m, pickups):
    df_map = pd.DataFrame({
        'poly': [Polygon(xy) for xy in m.nyc],
        'zone_id': [zone['LocationID'] for zone in m.nyc_info]})
    df_map['area_km'] = df_map['poly'].map(lambda x: x.area) / 1000000
    area_map = df_map.groupby(['zone_id'])['area_km'].sum()
    count = 0
    fig = plt.figure()
    cmap = plt.get_cmap('Greys_r')
    color_map = np.zeros(len(df_map['poly']))
    pickup_map = {}
    #for date in pickups.keys():
    #    for time in xrange(len(pickups[date])):
    plt.clf()
    norm = Normalize()
    date = '2015-05-02'
    time = 24
    pickups_count = pickups[date][time]
    for i in xrange(len(pickups_count) - 2):
        index = i + 1
        if index in LOCATIONID_MAP.keys():
            pickup_map[LOCATIONID_MAP[index]] += pickups_count[i]
        else:
            pickup_map[index] = pickups_count[i]

    for i in xrange(len(m.nyc_info)):
        index = m.nyc_info[i]['LocationID']
        if index in LOCATIONID_MAP.keys():
            color_map[i] = pickup_map[LOCATIONID_MAP[index]]
        else:
            color_map[i] = pickup_map[index]

    ax = fig.add_subplot(111, frame_on=False, xticks=[], yticks=[])
    df_map['patches'] = [PolygonPatch(x, fc='white', ec='grey', lw=.25, alpha=1.0,
                                      zorder=4) for x in df_map['poly']]
    pc = PatchCollection(df_map['patches'].values, match_original=True)
    pc.set_facecolor(cmap(norm(color_map)))
    ax.add_collection(pc)
    min_x, min_y = m(lower_left[0], lower_left[1])
    max_x, max_y = m(upper_right[0], upper_right[1])
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    ax.set_aspect(1)
    plt.tight_layout()
    fig.set_size_inches(16.76, 16.88)
    plt.savefig('data2/heat_map/nyc-' + str(date) + '-' + str(time) + '.png', dpi=100, alpha=True)
    count += 1
    if count % 100 == 0:
        print count




if __name__ == '__main__':
    main()
    root = tk.Toplevel()
    Uber_figure(root).pack(side="top", fill="y", expand="false")
    root.mainloop()
