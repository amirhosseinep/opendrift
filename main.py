'''
For multiple generation, you can use main_inputfile.py
'''
from opendrift.readers import reader_netCDF_CF_generic  
from opendrift.models.leeway import Leeway  
from datetime import timedelta  
import numpy as np  
from opendrift.readers import reader_global_landmask 
import sys
import matplotlib.pyplot as plt
from netCDF4 import Dataset  
import re 
'''
# Replace with your actual file path  
file_path = './tests/test_data/AmirDL/Data1/*.nc'  

with Dataset(file_path, 'r') as nc:  
    print("Variables in the file:")  
    for var in nc.variables:  
        print(var)
#sys.exit() 
'''
# Initiate a Leeway model  
o = Leeway(loglevel=20)  
object_type = 4
name = "test1-obt4-BOAT-1"
# Ocean model for current  
reader_ocean = reader_netCDF_CF_generic.Reader(o.test_data_folder() +   
    '/AmirDL/Data1/*.nc')  

# Wind data  
reader_arome = reader_netCDF_CF_generic.Reader(o.test_data_folder() +
    '/AmirDL/Data1/wind/*.nc') 

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
o.seed_elements(lon=-47.2045, lat=49.17851, radius=100, number=5000,  
                time=seeding_time, object_type=object_type)  

# Run the model  
o.run(duration=timedelta(hours=20), time_step=300, time_step_output=300)#, outfile='my_leeway_output.nc')  
fname = name+'.drift'
o.export_ascii(fname)
# Print and plot results  
print(o)  
#o.plot()  
#o.animation()
#%%
# Print and plot results
#print(o)
#o.plot(fast=True)
# Plot without displaying  
fig, ax = o.plot(show=False)  #fast=True,

# Get the figure associated with these GeoAxes  
fig = ax.get_figure()  

# Now save the figure as desired  
fig.savefig(f'{name}_plot.png', dpi=300, bbox_inches='tight')  

# Close the figure if you're scripting multiple plots  
plt.close(fig)  
#%%
# Animation with current as background.
# Note that drift is also depending on wind, which is not shown.
#o.animation(background=['x_sea_water_velocity', 'y_sea_water_velocity'],
#             skip=5,  # show every 5th vector
#             cmap=cmocean.cm.speed, vmin=0, vmax=.8, bgalpha=.7, land_color='#666666', fast=True)

#%%
# .. image:: /gallery/animations/example_leeway_0.gif



#%%
# Plot density of stranded elements
#d, dsub, dstr, lon, lat = o.get_density_array(pixelsize_m=3000)
#strand_density = xr.DataArray(dstr[-1,:,:], coords={'lon_bin': lon[0:-1], 'lat_bin': lat[0:-1]})
#print(strand_density)
#o.plot(fast=True, background=strand_density.where(strand_density>0),
#       vmin=0, vmax=20, cmap=cmocean.cm.dense, clabel='Density of stranded elements',
#       show_elements=False, linewidth=0)

def process_file(input_file, output_file):  
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:  
        lines = infile.readlines()  
        
        i = 0  
        while i < len(lines):  
            line = lines[i]  
            if not line.startswith('#'):  
                # Replace [content] with content  
                line = re.sub(r'\[(.*?)\]', r'\1', line)  
                
                # Split date and time with a tab  
                line = re.sub(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})', r'\1\t\2', line)  
                
                # Replace spaces between alphabet characters with tabs  
                line = re.sub(r'([a-zA-Z])\s+([a-zA-Z])', r'\1\t\2', line)  

                # Special handling for meanLon and meanLat  
                if 'meanLon' in line:  
                    parts = line.split()  
                    if len(parts) == 3:  
                        line = f"{parts[0]}\t{parts[1]}\t{parts[2]}\n"  
                
                # Special handling for seedDuration and seedSteps  
                if 'seedDuration' in line and 'seedSteps' in line:  
                    next_line = lines[i+1] if i+1 < len(lines) else ""  
                    if next_line.strip():  
                        values = next_line.split()  
                        if len(values) == 2:  
                            line = f"seedDuration\tseedSteps\n"  
                            outfile.write(line)  
                            line = f"{values[0]}\t{values[1]}\n"  
                            i += 1  # Skip the next line as we've processed it here  
            
            outfile.write(line)  
            i += 1  

input_file = fname
output_file = 'res-'+name+'.drift' 
process_file(input_file, output_file)