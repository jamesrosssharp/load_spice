#
#
#   Load ngspice files
#
#   (Since none of the python modules I tried worked)
#
#

import re
import struct
import numpy as np

#
#   ngspice Format:
#
#   Title: <title>
#   Date: Sat Nov 16 17:49:27  2024
#   Plotname: Operating Point
#   Flags: real
#   No. Variables: 214
#   No. Points: 1
#   Variables:
#   	0	v(temperat)	voltage
#   	190	i(vvdd)	current
#   Binary:
#   <binary data blob>

#   Dictionary format:
#
#{  
#   'plot_name': 'AC Analysis', 
#   'num_vars': 39, 
#   'num_points': 101, 
#   'vars': [['0', 'frequency', 'frequency grid=3'], ...], 
#   'data': {'frequency': array([1.00000000e+00+0.j, ...])}
# }
#

def load_spice(raw_file_path):

    plots = []
    with open(raw_file_path, "rb") as f:
        l = f.readline()
        num_points = 0
        num_vars   = 0
        plot_name  = ""
        flags = ""
        var_names = []
        while l != b'':
 
            #try:
            if 1:
                s = l.decode("ascii")

                pattern = (
                        r"Plotname:\s*(?P<plotname>\w.*\w)\s*|"
                        r"No\. Variables:\s*(?P<no_vars>\d+)\s*|"
                        r"No\. Points:\s*(?P<no_points>\d+)\s*|"
                        r"Flags:\s*(?P<flags>.*)\s*"
                    )
                m = re.search(pattern, s)
               

                if m is not None:

                    if m.groupdict()['no_vars'] is not None:
                        num_vars = int(m.groupdict()['no_vars'])

                    if m.groupdict()['no_points'] is not None:
                        num_points = int(m.groupdict()['no_points'])  

                    if m.groupdict()['plotname'] is not None:
                        plot_name = m.groupdict()['plotname']
            
                    if m.groupdict()['flags'] is not None:
                        flags = m.groupdict()['flags']

                if re.match(r"Variables:\s*", s) is not None:
                    var_names = []
                    for i in range(0,num_vars):
                        v = f.readline().decode("ascii").rstrip()
                        var_names.append(v.split("\t")[1:])

                if s == "Binary:\n":

                    dat = {}

                    # Struct unpack the points
                    if flags == "complex":
                        for v in var_names:
                            dat[v[1]] = np.zeros(num_points, dtype=complex)

                        for i in range(0, num_points):
                            raw_data = f.read(num_vars*16)
                            dat_list = (struct.unpack("d"*num_vars*2, raw_data)) 
                            for j, v in enumerate(var_names):
                                dat[v[1]][i] = dat_list[j*2] + 1j*dat_list[j*2+1]

                    elif flags == "real":

                        for v in var_names:
                            dat[v[1]] = np.zeros(num_points)

                        for i in range(0, num_points):
                            raw_data = f.read(num_vars*8)
                            dat_list = (struct.unpack("d"*num_vars, raw_data)) 
                            for j, v in enumerate(var_names):
                                dat[v[1]][i] = dat_list[j]


                    plots.append({"plot_name": plot_name, "num_vars": num_vars, "num_points": num_points, "vars": var_names, "data": dat})
                    

            l = f.readline()

        return plots





