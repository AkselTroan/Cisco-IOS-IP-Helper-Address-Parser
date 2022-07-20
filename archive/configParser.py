from ciscoconfparse import CiscoConfParse
import time, sys, os


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


class SVI:
    # hostname is the name of the router which the SVI is on
    # InterfaceName is the SVI (example: Vlan500)
    # IPHelperAddr is a list of ip helper-address that the SVI has
    def __init__(self, hostname, interfaceName):
        self.hostname = hostname
        self.interfaceName = interfaceName
        self.IPHelperAddr = []
    
    def addIPHelperAddr(self, addr):
        self.IPHelperAddr.append(addr)



def initArgParser():

    if not os.path.isfile(sys.argv[1]):
        print(f'{sys.argv[1]} does not exist')
        sys.exit()

    elif not os.path.isfile(sys.argv[2]):
        print(f'{sys.argv[2]} does not exist')
        sys.exit()

    elif len(sys.argv) != 3:
        print("usage: configParser.py <template-config> <running-config>")
        sys.exit()

    elif sys.argv[1] == sys.argv[2]:
        print("Config files has the same name")
        sys.exit()
    
    elif not os.path.isfile(sys.argv[1]) and os.path.isfile(sys.argv[2]):
        print("config file(s) does not exist")
        sys.exit()

    else:
        template = sys.argv[1]
        running = sys.argv[2]
    
    return ("./" + template), ("./" + running)



def readConfigFile(path):
    parse = CiscoConfParse(path, syntax='ios')
    return parse

def interpretTemplateConfig(parse):

    template_SVIs = []

    # First interpret the template and store it a correct
    for intf_obj in parse.find_objects('^interface Vlan'):  # Find all every parent which starts with interface vlan.

        intf_name = intf_obj.re_match_typed('^interface\s+(\S.+?)$')

        svi = SVI("__template__", intf_name) # Declaring a SVI object


        # Iterate all children on the interface and check if it is a helper-addresse
        for child in intf_obj.children:
            ip_helper_addr = child.re_match_typed(
            r'ip\shelper-address\s(\d+\.\d+\.\d+\.\d+)', result_type=str, default='__no_match__')
            
            if ip_helper_addr == "__no_match__":  # If the read child is not ip helper-address
                pass
            else:
                # Found a IP Helper Address
                #all_addr.append(ip_helper_addr)
                svi.addIPHelperAddr(ip_helper_addr)
        template_SVIs.append(svi)

    return template_SVIs


def interpretRunningConfig(parse):

    running_SVIs = []
    global_obj = parse.find_objects(r'^hostname')[0]
    hostname = global_obj.re_match_typed(r'^hostname\s+(\S+)', default='__no_hostname__')

    print("Hostname: " + hostname)
    for intf_obj in parse.find_objects('^interface Vlan'):  # Find all every parent which starts with interface vlan.
        intf_name = intf_obj.re_match_typed('^interface\s+(\S.+?)$')
        svi = SVI(hostname, intf_name) # Declaring a SVI object


        # Iterate all children on the interface and check if it is a helper-addresse
        for child in intf_obj.children:
            ip_helper_addr = child.re_match_typed(
            r'ip\shelper-address\s(\d+\.\d+\.\d+\.\d+)', result_type=str, default='__no_match__')
            
            if ip_helper_addr == "__no_match__":  # If the read child is not ip helper-address
                pass
            else:
                # Found a IP Helper Address
                svi.addIPHelperAddr(ip_helper_addr)
        running_SVIs.append(svi)

    return running_SVIs


def compareConfigs(template, running):
    

    # To visualize 
    # template_intfName = ["a", "b", "c"]
    # running_intfName = ["b", "a", "c"]
    # We can run if sviName is in, how we do not get the index.
    # Therefore we iterate through the whole list and store the indexes in a dictionary

    template_intfName = [] # The name will be stored in the order they are presented in the config
    template_indexes = {}
    i = 0
    
    for svi in template:
        template_intfName.append(svi.interfaceName)
        template_indexes[svi.interfaceName] = i
        # Ex_ template_indexes["Vlan500"] = 2
        i += 1
    
    running_intfName = [] # The name will be stored in the order they are presented in the config
    running_indexes = {}
    j = 0
    for svi in running:
        running_intfName.append(svi.interfaceName)
        running_indexes[svi.interfaceName] = j
        j += 1


    # We now have a list of all interfaceNames and the index that they are located at the global SVI object list
    
    # Check if the all the interface vlans are present. 
    # Two loops are required. Check if all SVIs in the template are in the running config
    # And all Vlans are in the template and report to the user the findings of interface Vlans runinng which is not in the template

    temp_missing_svi = []
    print("\nComparing the template with the running config")
    for svi in template:
        print("\n")
        # Check if the Vlan is in the running config:
        # If yes where is it located in the object list, and then check the IP helper addresses
        if svi.interfaceName in running_intfName:
            k = 0
            for name in running_intfName:
                if svi.interfaceName == running_intfName[k]:
                    print(colors.BOLD + colors.GREEN + "Found SVI: " + name + colors.ENDC)
                    temp_ind = template_indexes[name]
                    running_ind = running_indexes[name]
                    
                    # svi.IPHelperAddr and running[k].IPHelperAddr is the correct interfaces
                    for helper in  svi.IPHelperAddr:
                        if helper in running[k].IPHelperAddr:
                            for helper2 in running[k].IPHelperAddr:
                                if helper == helper2:
                                    print(colors.GREEN + "Found IP Helper Address: " + helper + colors.ENDC)
                        else:
                            print(colors.FAIL + "Could not find address: " + helper + colors.ENDC)
                    k += 1
                else:
                    k += 1
        else:
            temp_missing_svi.append(svi.interfaceName)
            print(colors.BOLD + colors.FAIL + "Missing interface: " + svi.interfaceName + colors.ENDC)
    
                    


    running_missing_svi = []
    print("\n" + colors.CYAN + "Comparing the running config with the template" + colors.ENDC)
    for svi in running:
        print("\n")
        # Check if the Vlan is in the running config:
        # If yes where is it located in the object list. and then check the IP helper addresses
        if svi.interfaceName in template_intfName:
            k = 0
            for name in template_intfName:
                if svi.interfaceName == template_intfName[k]:
                    print(colors.BOLD + colors.GREEN + "Found SVI: " + name + colors.ENDC)
                    temp_ind = template_indexes[name]
                    running_ind = running_indexes[name]
                    
                    # svi.IPHelperAddr and running[k].IPHelperAddr is the correct interfaces
                    for helper in  svi.IPHelperAddr:
                        if helper in template[k].IPHelperAddr:
                            for helper2 in template[k].IPHelperAddr:
                                if helper == helper2:
                                    print(colors.GREEN + "Found IP Helper Address: " + helper + colors.ENDC)
                        else:
                            print(colors.FAIL + "Could not find address: " + helper + colors.ENDC)
                    k += 1
                else:
                    k += 1
        else:
            running_missing_svi.append(name)
            print(colors.BOLD + colors.FAIL + "Missing interface: " + svi.interfaceName + colors.ENDC)        


def main():

    # Fetch and validate arguments
    template_path, running_path = initArgParser()

    # Start timer
    start = time.perf_counter()

    # Interpret the given template with correct IP Helper Addresses
    template_parser = readConfigFile(template_path)
    template_SVIs = interpretTemplateConfig(template_parser)

    # Parse the running config file
    parser = readConfigFile(running_path)
    running_SVIs = interpretRunningConfig(parser)

    # Compare the two configurations
    compareConfigs(template_SVIs, running_SVIs)
        
    # Stop timer
    stop = time.perf_counter()

    print(f"Total time to read and compare config: {stop - start:0.4f} seconds")


if __name__ == "__main__":
    main()
