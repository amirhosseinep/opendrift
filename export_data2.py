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
    f.write('2019-04-12\t13:33:46\tGSHHS\n')
    f.write('# Model version:\n')
    f.write('modelVersion\n')
    f.write('2.50\n')
    f.write('# Object class id & name:\n')
    f.write('objectClassId\tobjectClassName\n')
    f.write('26\tLIFE-RAFT-DB11\n')
    f.write('# Life raft capacity & search object length:\n')
    f.write('lifeRaftCapacity\tsearchObjectLength\n')
    f.write('6\t1\n')
    f.write('# Number of route points\n')
    f.write('numRoutePoints\n')
    f.write('1\n')

    # Loop through time steps
    for i, date in enumerate(dates):
        f.write('# Date [UTC]:\n')
        f.write('nowDate\tnowTime\n')
        f.write(f'{date.strftime("%Y-%m-%d")}\t{date.strftime("%H:%M:%S")}\n')
        f.write('# Time passed [min] & [timesteps], now seeded, seeded so far:\n')
        f.write('timePassed\tnStep\tnowSeeded\tnSeeded\n')
        f.write(f'{i*300}\t{i+1}\t0\t5000\n')  # 300 is the time step in seconds

        # Mean position
        mean_lon = lons[:, i].mean()
        mean_lat = lats[:, i].mean()
        f.write('# Mean position:\n')
        f.write('meanLon\tmeanLat\n')
        f.write(f'{mean_lon:.4f}\t{mean_lat:.4f}\n')

        # Particle data
        f.write('# Particle data:\n')
        f.write('id\tlon\tlat\tstate\tage\torientation\n')
        for j in range(lons.shape[0]):
            f.write(f'{j+1}\t{lons[j, i]:.4f}\t{lats[j, i]:.4f}\t11\t0\t1\n')

# Close the file
nc_file.close()