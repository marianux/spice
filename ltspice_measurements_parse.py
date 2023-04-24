import re
import pandas as pd
import os
import sys

logfilename = sys.argv[1]
csvfilename = os.path.splitext(logfilename)[0] + '.csv'

step = 0
data = [];

logfile = open(logfilename,'r', encoding = "ISO-8859-1")

def match_step(line):
    return re.match(r'\.step (.*)', line)

# find first .step definition
for line in logfile:    
    match = match_step(line)
    if match:
        break

# iterate through all steps with parameters
# while match:
#     step += 1
#     row = { 'step': step }

#     parameters = match.group(1).split()
#     for p in parameters:
#         [key, value] = p.split('=')
#         row[key] = value
    
#     data.append(row)
#     match = match_step(next(logfile))

# iterate through measurement definitions
for line in logfile:    
    match = re.match(r'Measurement: (.*)', line)
    if match:  
        name = match.group(1)
        
        # row with column details
        col_names = next(logfile).split()
        
        col_names = [ col_names[0], name]

        # iterate through measurement results for each step
        while True:
            measurement = next(logfile).split()
            if not measurement:
                break
            row = dict(zip(col_names, measurement[:2] ))
            
            data.append(row)

logfile.close()

frame = pd.DataFrame(data).set_index('step').groupby('step').first()

# format conversion
pattern_float = r"[-+]?\d*\.\d+"
pattern_db = r'([\d.]+)dB'


for cols in frame.columns:
    
    # Extract the modulus from col1 using regular expressions
    modulus_str = frame[cols].apply(lambda x: re.findall(pattern_db, x)[0] if re.findall(pattern_db, x) else None)
    
    if not all(x is None for x in modulus_str):
        #Some elements are not None
        
        # Convert the modulus from dB to linear units
        replace_val = 10 ** (modulus_str.astype(float) / 20)
        
    else:
        #All elements are None
        modulus_str = frame[cols].apply(lambda x: re.findall(pattern_float, x)[0] if re.findall(pattern_float, x) else None)
        replace_val = modulus_str.astype(float)
        
    # Convert col1 to a float column, excluding the dB suffix
    frame[cols] = replace_val

    
frame.to_csv(csvfilename)
