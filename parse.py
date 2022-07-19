from ciscoconfparse import CiscoConfParse
from init.initArgParser import initArgParser
from init.svi import SVI
from file_handlers.read_files import read_bad_addresses, readConfigFile, read_list
from file_handlers.interpret_running_config import interpretRunningConfig
from file_handlers.pan import test, coll
import time, sys, os
import pandas as pd


class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



def main():
      # Fetch and validate arguments
    running_path = initArgParser()

    # Start timer
    start = time.perf_counter()

    # Declare bad addresses
    
    di = {"Hostname": [],
            "Interface": [],
            "VRF": [],
            "IPHA": [],
            "Status": []}
    running_configs = read_list(running_path)
    for config in running_configs:

        parser = readConfigFile(config)
        hostname, svi ,vrf, ipha, status = interpretRunningConfig(parser, read_bad_addresses())
        di['Hostname'] = di['Hostname'] + hostname
        di['Interface'] = di['Interface'] + svi
        di['VRF'] = di['VRF'] + vrf
        di['IPHA'] = di['IPHA'] + ipha
        di['Status'] = di['Status'] + status 
    test = pd.DataFrame(di)

    print(test)   #analyseConfig(req, host)


if __name__ == "__main__":
    main()
