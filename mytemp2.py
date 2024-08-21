from netCDF4 import Dataset  
import shutil  
from opendrift.readers import reader_netCDF_CF_generic  
from opendrift.models.leeway import Leeway  
from datetime import timedelta  
import numpy as np  

with Dataset('./tests/test_data/AmirDL/cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H_2024010602_R20240105T12_14.nc', 'r') as nc:  
    time_var = nc.variables['time']  
    print("Time variable:", time_var)  
    print("Number of time steps:", len(time_var))  
    print("Time values:", time_var[:])  
    
    if hasattr(time_var, 'units'):  
        print("Time units:", time_var.units)  
    
    if hasattr(time_var, 'calendar'):  
        print("Calendar:", time_var.calendar)
#sys.exit()
###########

# Path to your original file  
original_file = './tests/test_data/AmirDL/SMOC_20240101_R20240110.nc' 

# Path for the new modified file  
modified_file = './tests/test_data/AmirDL/SMOC_20240101_R20240110_modified.nc'  

# Create a copy of the original file  
shutil.copy(original_file, modified_file)  

# Open the copied file in read-write mode  
with Dataset(modified_file, 'r+') as nc:  
    # Rename 'utotal' to 'x_sea_water_velocity'  
    nc.renameVariable('utotal', 'x_sea_water_velocity')  
    
    # Rename 'vtotal' to 'y_sea_water_velocity'  
    nc.renameVariable('vtotal', 'y_sea_water_velocity')  
    
    # Update attributes if necessary  
    nc.variables['x_sea_water_velocity'].long_name = 'Eastward sea water velocity'  
    nc.variables['x_sea_water_velocity'].standard_name = 'eastward_sea_water_velocity'  
    nc.variables['y_sea_water_velocity'].long_name = 'Northward sea water velocity'  
    nc.variables['y_sea_water_velocity'].standard_name = 'northward_sea_water_velocity'  

print("File modified successfully.")

with Dataset(modified_file, 'r') as nc:  
    print("Variables in the file:")  
    for var in nc.variables:  
        print(f"{var}:")  
        print(f"  Dimensions: {nc.variables[var].dimensions}")  
        print(f"  Shape: {nc.variables[var].shape}")  
        print(f"  Attributes:")  
        for attr in nc.variables[var].ncattrs():  
            print(f"    {attr}: {nc.variables[var].getncattr(attr)}")  
        print()  
############
# Initiate a Leeway model  
o = Leeway(loglevel=20)  

# Ocean model for current  
reader_ocean = reader_netCDF_CF_generic.Reader(o.test_data_folder() +   
    '/AmirDL/SMOC_20240101_R20240110_modified.nc')  

reader_ocean.variables = {'x_sea_water_velocity': 'uo',  
                          'y_sea_water_velocity': 'vo'}
# Wind data  
reader_arome = reader_netCDF_CF_generic.Reader(o.test_data_folder() +  
    '/AmirDL/cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H_2024010602_R20240105T12_14.nc')  
# Map the wind variable names  
reader_arome.variables = {'x_wind': 'Eastward wind (WIND)',  
                          'y_wind': 'Northward wind (WIND)'}  
# Add readers to the model  
o.add_reader([ reader_ocean, reader_arome])  

# Manually specify the variable names  
'''
reader_ocean.variable_mapping = {  
    'x_sea_water_velocity': 'utotal',  # Total eastward velocity  
    'y_sea_water_velocity': 'vtotal',  # Total northward velocity  
    'x_sea_water_velocity_tidal': 'utide',  # Eastward tidal velocity  
    'y_sea_water_velocity_tidal': 'vtide',  # Northward tidal velocity  
    'eastward_stokes_drift': 'vsdx',  # Eastward Stokes drift  
    'northward_stokes_drift': 'vsdy'  # Northward Stokes drift  
}  
'''
print("\nRequired variables for the model:")  
print(o.required_variables)  

# Set the seeding time  
seeding_time = reader_ocean.start_time

# Seed elements  
o.seed_elements(lon=4.52, lat=59.7, radius=100, number=5000,  
                time=seeding_time, object_type=26)  
print("Ocean data start time:", reader_ocean.start_time)  
print("Ocean data end time:", reader_ocean.end_time)  
print("Seeding time:", seeding_time)  
print("Simulation end time:", seeding_time + timedelta(hours=24))

print("Ocean data time range:", reader_ocean.start_time, "to", reader_ocean.end_time)  
print("Wind data time range:", reader_arome.start_time, "to", reader_arome.end_time)
print("Ocean data coverage:", reader_ocean.coverage_string)  
print("Wind data coverage:", reader_arome.coverage_string)
# Run the model  
o.run(duration=timedelta(hours=2), time_step=300, time_step_output=300, outfile='my_leeway_output.nc')  

# Print and plot results  
print(o)  
o.plot()  
o.animation()
#%%
# Print and plot results
print(o)
o.export_ascii('drift_output.drift')
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
