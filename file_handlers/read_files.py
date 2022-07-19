from ciscoconfparse import CiscoConfParse
def read_bad_addresses():  
    file = open("./bad-addresses", "r")
    content_list = file.readlines()  

    bad_addresses = []
    i = 0

    for lines in content_list: 
        current_line = lines.replace(" ", "").replace("\n", "").split("#")
        bad_addresses.append(current_line[0])
        i += 1
    return bad_addresses


def readConfigFile(path):
    parse = CiscoConfParse(path, syntax='ios')
    return parse


def read_list(path):  
    file = open(path, "r")
    content_list = file.readlines()  

    configs = []
    i = 0

    for lines in content_list: 
        current_line = lines.replace(" ", "").replace("\n", "").split("#")
        configs.append(current_line[0])
        i += 1
    return configs