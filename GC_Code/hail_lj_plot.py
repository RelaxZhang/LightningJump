# Standard libraries
from netCDF4 import Dataset
import numpy as np
from matplotlib import pyplot as plt
import cftime
import sys
import cartopy.crs as ccrs
from matplotlib.patches import Rectangle
import math
import numpy.ma as ma
import pandas as pd
from collections import Counter
from dateutil import parser
from shapely.geometry import Point
from shapely.geometry import MultiPoint
from shapely.geometry.polygon import Polygon
from datetime import datetime, timedelta, time
# Configuration
level2_root = '/g/data/rq0/level_2'
radar_id = '53' #see the reference file for all radars: https://dapds00.nci.org.au/thredds/fileServer/rq0/radar_site_list.csv
date_str = '20210929' #format of YYYYMMDD
timestep_range = 288 #timestep in file to access data
var_name = 'shi' #reflectivity is the reflectivity at an altitude of 2.5km above the radar site, see reference file for radar altitude.
lj_num = "Lightning Jump 0"
# Load data

level2_ffn = level2_root+'/'+radar_id+'/'+var_name.upper()+'/'+radar_id+'_'+date_str+'_'+var_name+'.nc'
with Dataset(level2_ffn, mode='r') as fh:
    
 #coordinate of LJ   
    latitude =  -29.277534721590918
    longitude = 149.49823086363642








	

#looping over 50 minute timeframe
    for i in range(118, 118+10):

        refl_data_temp = fh.variables[var_name][i,:,:]
        # print('zzz',np.shape(fh.variables[var_name]))
        mask = refl_data_temp.data > 0
        # print('XXX',(refl_data_temp.data[mask]))
        nsteps = fh.variables[var_name].shape[0]        #'''I've just change the assigned value to nsteps with shape rather than magic number [:, 1, 1]'''
        lenmaskarray = len(refl_data_temp.data[mask])
        # print('len',nsteps,lenmaskarray)

        if i > nsteps:
            print('timestep index is beyond the number of time step')
            sys.exit()

        if lenmaskarray > 3:   
            refl_data = fh.variables[var_name][i,:,:]
            # print('shape',np.shape(refl_data))
            time_step = fh.variables['time'][i]
            time_step = cftime.num2date(fh.variables['time'][i], fh.variables['time'].getncattr('units'))
            lat_grid = fh.variables['latitude'][:]
            lon_grid = fh.variables['longitude'][:]
            #print(np.min(lon_grid), np.max(lon_grid), np.min(lat_grid), np.max(lat_grid))
            

        # Create figure only if more than X(3) number of points
        if lenmaskarray > 3:
            extent = (np.min(lon_grid), np.max(lon_grid), np.min(lat_grid), np.max(lat_grid))
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})  
            ax.set_extent(extent, ccrs.PlateCarree())
            ax = plt.axes(projection=ccrs.PlateCarree())
            plt.contourf(lon_grid, lat_grid, refl_data, np.arange(0,61),transform=ccrs.PlateCarree())
         #adding location of LJ  
            ax.scatter(longitude, latitude ,color = "red", transform=ccrs.PlateCarree())
         #adding box around LJ 1x1 degrees 
            rect = Rectangle((longitude - 0.5, latitude - 0.5), 1, 1, edgecolor='red', facecolor='none')
            ax.add_patch(rect)
            plt.colorbar(location = 'left', shrink = 0.4)
            plt.title(time_step)
            ax.coastlines()



            #'''All the plots will be stored under the path radar_plot/radar_plot_x_timestep/png, x refers to the timestep at the current stage'''
            plt.savefig('Bourke_lj_hail/Cluster0/LJ_14/' + 'radar_plot_' + str(i) + "_timestep.png")