import netCDF4 as nc
import pandas as pd

# Open the NetCDF file
nc_file = nc.Dataset('my_leeway_output.nc', 'r')

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

# Create the output text file
with open('drift_output.txt', 'w') as f:
    # Header section
    f.write('# Drift simulation initiated [UTC]:\n')
    f.write('simDate\tsimTime\n')
    f.write(f'{dates[0].strftime("%Y-%m-%d")}\t{dates[0].strftime("%H:%M:%S")}\n')
    f.write('# Total number of steps\n')
    f.write('totalSteps\n')
    f.write(f'{len(dates)}\n')

    # Loop through time steps
    for i, date in enumerate(dates):
        f.write('# Date [UTC]:\n')
        f.write('nowDate\tnowTime\n')
        f.write(f'{date.strftime("%Y-%m-%d")}\t{date.strftime("%H:%M:%S")}\n')
        f.write('# Time passed [min] & [timesteps], now seeded, seeded so far:\n')
        f.write('timePassed\tnStep\tnowSeeded\tnSeeded\n')
        f.write(f'{i*300}\t{i+1}\t10\t{i*10+10}\n')  # 300 is the time step in seconds

        # Mean position
        mean_lon = lons[:, i].mean()
        mean_lat = lats[:, i].mean()
        f.write('# Mean position:\n')
        f.write('meanLon\tmeanLat\n')
        f.write(f'{mean_lon:.4f}\t{mean_lat:.4f}\n')

        # Particle data
        f.write('# Particle data:\n')
        f.write('nStep\tid\tlon\tlat\n')
        for j in range(lons.shape[0]):
            f.write(f'{i+1}\t{j+1}\t{lons[j, i]:.4f}\t{lats[j, i]:.4f}\n')

# Close the file
nc_file.close()