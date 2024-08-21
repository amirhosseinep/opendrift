import re  

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

input_file = '/home/aesmaeilpour/Documents/Amir_home_project/Git/open drift 2/opendrift/tests/test_data/AmirDL/CM2/CM2.drift'  # Replace with your input file name  
output_file = 'res-CM2.drift'  # Replace with your desired output file name  
process_file(input_file, output_file)
