# Standard libraries
from netCDF4 import Dataset
import numpy as np
from matplotlib import pyplot as plt
import cftime
import sys
import cartopy.crs as ccrs
import xarray as xr
######## code to plot timeseries of SHI data ##########
# Configuration
level2_root = '/g/data/rq0/level_2'
radar_id = '22' #see the reference file for all radars: https://dapds00.nci.org.au/thredds/fileServer/rq0/radar_site_list.csv
date_str = '20211019' #format of YYYYMMDD
timestep_range = 286 #timestep in file to access data
var_name = 'shi' #reflectivity is the reflectivity at an altitude of 2.5km above the radar site, see reference file for radar altitude.

longitude =  148.604052
latitude = -20.766897


# Load data
level2_ffn = level2_root+'/'+radar_id+'/'+var_name.upper()+'/'+radar_id+'_'+date_str+'_'+var_name+'.nc'
with Dataset(level2_ffn, mode='r') as fh:
    # print the vairables
     #print('xxx',var_name,timestep)
    # print(np.shape(fh.variables[var_name]))

    for i in range(timestep_range):

        refl_data_temp = fh.variables[var_name][i,:,:]
        nsteps = fh.variables[var_name].shape[0]        #'''I've just change the assigned value to nsteps with shape rather than magic number [:, 1, 1]'''
        
        # print('timestep index is beyond the number of time step')
        # sys.exit()
        refl_data = fh.variables[var_name][i,:,:]
        # print('shape',np.shape(refl_data))
        time_step = fh.variables['time'][i]
        time_step = cftime.num2date(fh.variables['time'][i], fh.variables['time'].getncattr('units'))
       # print('selected time is', time_step, 'UTC+0')
        lat_grid = fh.variables['latitude'][:]
        lon_grid = fh.variables['longitude'][:]
        
        if np.max(refl_data_temp) > 26.6:
            #print('selected time is', time_step, 'UTC+0')
            extent = (np.min(lon_grid), np.max(lon_grid), np.min(lat_grid), np.max(lat_grid))
            fig = plt.figure(figsize=(12, 20), facecolor='w')    
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.set_extent(extent, ccrs.PlateCarree())
            #ax.contourf(lons, lats, d, transform=ccrs.PlateCarree())
            plt.contourf(lon_grid, lat_grid, refl_data, np.arange(0,61),
                transform=ccrs.PlateCarree())
            plt.colorbar(shrink=0.4)

            ax.scatter(longitude, latitude ,color = "red", transform=ccrs.PlateCarree())
            plt.title(time_step)
            ax.coastlines()

    #'''All the plots will be stored under the path radar_plot/radar_plot_x_timestep/png, x refers to the timestep at the current stage'''
            plt.savefig('mackay_plot/' + 'radar_plot_' + str(i) + "_timestep.png")

        
            
            












