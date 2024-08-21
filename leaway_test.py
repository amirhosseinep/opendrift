'''
This code create a drift file with a format near to MSAR drift.
#reader_arome: This is a reader_netCDF_CF_generic.Reader object that reads wind data from an AROME (Aire limitée Adaptation dynamique Développement InterNational) atmospheric model.
#reader_norkyst: This is a reader_netCDF_CF_generic.Reader object that reads ocean current data from the NorKyst-800 ocean model.
'''


#!/usr/bin/env python
"""
Leeway
==================================
"""
from netCDF4 import Dataset  
from datetime import timedelta
import cmocean
import xarray as xr
from opendrift.readers import reader_netCDF_CF_generic
from opendrift.models.leeway import Leeway
from datetime import timedelta, datetime  

#modified_file = './tests/test_data/AmirDL/SMOC_20240101_R20240110.nc'  
#with Dataset(modified_file, 'r') as nc:  
#    print("Variables in the file:")  
#    for var in nc.variables:  
#        print(var)
o = Leeway(loglevel=0)  # Set loglevel to 0 for debug information
o.max_elements = 5000  # Set the maximum number of particles to 5000

# Atmospheric model for wind
#reader_arome = reader_netCDF_CF_generic.Reader('https://thredds.met.no/thredds/dodsC/mepslatest/meps_lagged_6_h_latest_2_5km_latest.nc')
reader_arome = reader_netCDF_CF_generic.Reader(o.test_data_folder() +
    '/AmirDL/CM1/wind-20240102/*.nc')

# Ocean model for current
#reader_norkyst = reader_netCDF_CF_generic.Reader('https://thredds.met.no/thredds/dodsC/mepslatest/meps_lagged_6_h_latest_2_5km_latest.nc')
reader_ocean = reader_netCDF_CF_generic.Reader(o.test_data_folder() +
    '/AmirDL/CM1/SMOC_20240101_R20240110.nc')

o.add_reader(reader_ocean)
o.add_reader(reader_arome)
# Set the seeding time  
seeding_time = max(reader_arome.start_time, reader_ocean.start_time)

#%%
# Seed leeway elements at defined position and time
object_type = 26  # 26 = Life-raft, no ballast
o.seed_elements(lon=4.56, lat=59.68, radius=100, number=5000,
                time=seeding_time, object_type=object_type)
#%%
# Running model
o.run(duration=timedelta(hours=10), time_step=241, time_step_output=241,outfile='my_leeway_output.nc')

#%%
# Print and plot results
print(o)
o.export_ascii('CM2.drift')
#%%
# Animation with current as background.
# Note that drift is also depending on wind, which is not shown.
#o.animation(background=['x_sea_water_velocity', 'y_sea_water_velocity'],
#             skip=5,  # show every 5th vector
#             cmap=cmocean.cm.speed, vmin=0, vmax=.8, bgalpha=.7, land_color='#666666', fast=True)

#%%
# .. image:: /gallery/animations/example_leeway_0.gif

o.plot(fast=True)

#%%
# Plot density of stranded elements
d, dsub, dstr, lon, lat = o.get_density_array(pixelsize_m=3000)
strand_density = xr.DataArray(dstr[-1,:,:], coords={'lon_bin': lon[0:-1], 'lat_bin': lat[0:-1]})
print(strand_density)
o.plot(fast=True, background=strand_density.where(strand_density>0),
       vmin=0, vmax=20, cmap=cmocean.cm.dense, clabel='Density of stranded elements',
       show_elements=False, linewidth=0)

