from init.initArgParser import initArgParser
from file_handlers.read_files import read_bad_addresses, readConfigFile, read_list
from file_handlers.interpret_running_config import interpretRunningConfig
from file_handlers.interpret_running_config import find_big_networks
import pandas as pd


def interpretAndSave():

    running_path = initArgParser()

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
        #find_big_networks(parser)
    df = pd.DataFrame(di)

    df.to_excel("./running-config.xlsx")


