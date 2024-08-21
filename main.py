from opendrift.readers import reader_netCDF_CF_generic  
from opendrift.models.leeway import Leeway  
from datetime import timedelta  
import numpy as np  
from opendrift.readers import reader_global_landmask 
import sys

from netCDF4 import Dataset  
'''
# Replace with your actual file path  
file_path = './tests/test_data/AmirDL/SMOC_20240101_R20240110.nc'  

with Dataset(file_path, 'r') as nc:  
    print("Variables in the file:")  
    for var in nc.variables:  
        print(var)
#sys.exit() 
'''
# Initiate a Leeway model  
o = Leeway(loglevel=20)  

# Ocean model for current  
reader_ocean = reader_netCDF_CF_generic.Reader(o.test_data_folder() +   
    '/AmirDL/CM3/SMOC_20240103_R20240117.nc')  

# Wind data  
reader_arome = reader_netCDF_CF_generic.Reader(o.test_data_folder() +
    '/AmirDL/CM3/wind-20240103-/*.nc') 

# Add readers to the model  
o.add_reader([ reader_ocean, reader_arome])  

print("\nRequired variables for the model:")  
print(o.required_variables)  

# Set the seeding time  
seeding_time = max(reader_arome.start_time, reader_ocean.start_time)  
print("Seeding time:", seeding_time)  
#print("Simulation end time:", seeding_time + timedelta(hours=24))
print("Ocean data time range:", reader_ocean.start_time, "to", reader_ocean.end_time)  
print("Wind data time range:", reader_arome.start_time, "to", reader_arome.end_time)
#sys.exit()
# Seed elements  
o.seed_elements(lon=4.86, lat=59.73, radius=100, number=5000,  
                time=seeding_time, object_type=26)  

# Run the model  
o.run(duration=timedelta(hours=20), time_step=300, time_step_output=300, outfile='my_leeway_output.nc')  
o.export_ascii('CM3.drift')
# Print and plot results  
print(o)  
o.plot()  
o.animation()
#%%
# Print and plot results
print(o)

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
#d, dsub, dstr, lon, lat = o.get_density_array(pixelsize_m=3000)
#strand_density = xr.DataArray(dstr[-1,:,:], coords={'lon_bin': lon[0:-1], 'lat_bin': lat[0:-1]})
#print(strand_density)
#o.plot(fast=True, background=strand_density.where(strand_density>0),
#       vmin=0, vmax=20, cmap=cmocean.cm.dense, clabel='Density of stranded elements',
#       show_elements=False, linewidth=0)

