'''
wind and ocean current source:
https://data.marine.copernicus.eu/product/WIND_GLO_PHY_L4_NRT_012_004/files?path=WIND_GLO_PHY_L4_NRT_012_004%2Fcmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H_202207%2F2024%2F07%2F&subdataset=cmems_obs-wind_glo_phy_nrt_l4_0.125deg_PT1H_202207
https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/files?path=GLOBAL_ANALYSISFORECAST_PHY_001_024%2Fcmems_mod_glo_phy_anfc_merged-uv_PT1H-i_202211%2F2024%2F07%2F&subdataset=cmems_mod_glo_phy_anfc_merged-uv_PT1H-i_202211
'''

import csv  
from opendrift.readers import reader_netCDF_CF_generic  
from opendrift.models.leeway import Leeway  
from datetime import timedelta  
import matplotlib.pyplot as plt  
import re  
from netCDF4 import Dataset  
import os  
#import logging
def run_leeway_simulation(name, ocean_file, wind_file, lon, lat, status_file,obj_type):  
    try:   
        # Set the logging level for all OpenDrift modules
        #logging.getLogger('opendrift').setLevel(logging.ERROR)
        o = Leeway(loglevel=20) #loglevel=20
        #o.set_config('general:buffer', 10)   
        # Ocean model for current  
        reader_ocean = reader_netCDF_CF_generic.Reader(o.test_data_folder()+ocean_file)  
        # Wind data  
        reader_arome = reader_netCDF_CF_generic.Reader(o.test_data_folder()+wind_file)  
        # Add readers to the model  
        o.add_reader([reader_ocean, reader_arome])  

        #print("\nRequired variables for the model:")  
        #print(o.required_variables)
        print("Current Obj type we use: "+str(obj_type))
        seeding_time = max(reader_arome.start_time, reader_ocean.start_time)  
        print("Seeding time:", seeding_time)  
        oc = f"{reader_ocean.start_time} to {reader_ocean.end_time}"  
        wind = f"{reader_arome.start_time} to {reader_arome.end_time}"
        o.seed_elements(lon=lon, lat=lat, radius=100, number=5000,  
                        time=seeding_time, object_type=obj_type)    
        o.run(duration=timedelta(hours=20), time_step=300, time_step_output=300)  
        
        output_dir = os.path.join('drift-outputs', name)  
        os.makedirs(output_dir, exist_ok=True)
        
        fname = os.path.join(output_dir, f'{name}.drift')  
        o.export_ascii(fname)

        fig, ax = o.plot(show=False)  #fast=True,   
        fig = ax.get_figure()  
        fig.savefig(os.path.join(output_dir,f'{name}_plot.png'), dpi=300, bbox_inches='tight')   
        plt.close(fig)    

        input_file = fname  
        output_file = os.path.join(output_dir, f'res-{name}.drift')
        # make it tab separated and make it MSar-compatible 
        process_file(input_file, output_file)  

        log_status(status_file, name, "Complete", "Simulation finished successfully",oc,wind, lon, lat)  

    except Exception as e:    
        log_status(status_file, name, "Failed", str(e), '','', lon, lat)  

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
                            i += 1 
            outfile.write(line)
            i += 1  

def log_status(status_file, name, status, remark, oc, wind, lon, lat):  
    # Append status information to the status file  
    with open(status_file, 'a', newline='') as csvfile:  
        writer = csv.writer(csvfile)  
        writer.writerow([name, status, remark, oc, wind, lon, lat])  

# Open CSV and loop through each row  
status_file = 'Running_status.csv'  
with open(status_file, 'w', newline='') as csvfile:  
    writer = csv.writer(csvfile)  
    writer.writerow(['Name', 'Status', 'Remark', 'Ocsean Current time range','Wind time range', 'Start Longitude', 'Start Latitude'])  

with open('input_parameters.csv', newline='') as csvfile:  
    reader = csv.DictReader(csvfile)  
    for row in reader:  
        name = row['name']  
        ocean_file = row['ocean_file']  
        wind_file = row['wind_file']
        lon = float(row['lon'])  
        lat = float(row['lat'])
        obj_type = int(row['object_type'])

        # Run the model for this set of parameters  
        run_leeway_simulation(name, ocean_file, wind_file, lon, lat, status_file, obj_type)