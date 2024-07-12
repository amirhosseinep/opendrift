import netCDF4 as nc
import pandas as pd

# Open the NetCDF file
nc_file = nc.Dataset('leeway_output.nc', 'r')

# Access specific variables
lons = nc_file.variables['lon'][:]
lats = nc_file.variables['lat'][:]
times = nc_file.variables['time'][:]

# Convert times to datetime objects
time_units = nc_file.variables['time'].units
try:
    time_calendar = nc_file.variables['time'].calendar
except AttributeError:
    time_calendar = 'standard'

dates = nc.num2date(times, units=time_units, calendar=time_calendar)
start_time = dates[0]

# Create the output DataFrame
output_data = []
for j in range(lons.shape[1]):  # Loop through time steps
    mean_lon = lons[:, j].mean()
    mean_lat = lats[:, j].mean()
    for i in range(lons.shape[0]):  # Loop through trajectories
        output_data.append({
            'time_step': j+1,
            'particle_id': i+1,
            'lon': lons[i, j],
            'lat': lats[i, j],
            'mean_lon': mean_lon,
            'mean_lat': mean_lat,
            'seeding_datetime': dates[j]
        })

output_df = pd.DataFrame(output_data)

# Save the DataFrame to a CSV file
output_df.to_csv('trajectory_data.csv', index=False)

# Close the file
nc_file.close()