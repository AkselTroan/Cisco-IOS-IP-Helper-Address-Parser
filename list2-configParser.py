from ciscoconfparse import CiscoConfParse
import time, sys, os, csv


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


class Host:

    def __init__(self, hostname, vlanIDs, vlanNames, SVIs):
        self.hostname = hostname
        self.vlanIDs = vlanIDs
        self.vlanNames = vlanNames
        self.SVIs = SVIs # List of SVI objects


class SVI:
    # hostname is the name of the router which the SVI is on
    # InterfaceName is the SVI (example: Vlan500)
    # IPHelperAddr is a list of ip helper-address that the SVI has
    def __init__(self, hostname, interfaceName):
        self.hostname = hostname
        self.vrf = ""
        self.interfaceName = "interface " + interfaceName
        self.IPHelperAddr = []
    
    def addIPHelperAddr(self, addr):
        self.IPHelperAddr.append(addr)


    def setVRF(self, vrf):
        self.vrf = vrf


class requirements:

    def __init__(self, vlans, ipha, vrfs, badAdresses):
        self.vlans = vlans
        self.ipha = ipha#.split(":") # vlan-name:addr1,addr2,addrX
        self.vrfs = vrfs#.split(":") # vlan-name:vrf-name
        self.badAddresses = badAdresses


def initArgParser():

    if not os.path.isfile(sys.argv[1]):
        print(f'{sys.argv[1]} does not exist')
        sys.exit()

    elif not os.path.isfile(sys.argv[2]):
        print(f'{sys.argv[2]} does not exist')
        sys.exit()

    elif len(sys.argv) != 3:
        print("usage: configParser.py <requirements file> <running-config/List of running-config files>")
        sys.exit()

    elif sys.argv[1] == sys.argv[2]:
        print("Submitted files has the same name")
        sys.exit()
    
    elif not os.path.isfile(sys.argv[1]) and os.path.isfile(sys.argv[2]):
        print("Submitted file(s) does not exist")
        sys.exit()

    else:
        req_path = sys.argv[1]
        running = sys.argv[2]
    
    return ("./" + req_path), ("./" + running)


def interpretRequirements(file):
    file = open(file, 'r')
    vlan_read = False
    ipha_read = False
    vrf_read = False
    badAddr_read = False
    vlans = []
    ipha = []
    vrf = []
    badAddr = []

    while True:
  
        line = file.readline()
  
        # if line is empty
        # end of file is reached
        if not line:
            break

        if line[0] == "#":
            print("Found a comment. Skipping...")
        
        else:
        
            if line.strip() == "[vlan]":
                vlan_read = True
                ipha_read = False
                vrf_read = False
                badAddr_read = False
        
            elif line.strip() == "[ip helper-address]":
                ipha_read = True
                vlan_read = False
                vrf_read = False
                badAddr_read = False

            elif line.strip() == "[vrf]":
                vrf_read = True
                vlan_read = False
                ipha_read = False
                badAddr_read = False

            elif line.strip() == "[bad-addresses]":
                vrf_read = False
                vlan_read = False
                ipha_read = False
                badAddr_read = True
        
            if line.strip() == "":
                vrf_read = False
                vlan_read = False
                ipha_read = False
                badAddr_read = False

            if vlan_read and line.strip()[0] != "[":
                vlans.append(line.strip())
        
            elif ipha_read and line.strip()[0] != "[":
                ipha.append(line.strip())
        
            elif vrf_read and line.strip()[0] != "[":
                vrf.append(line.strip())
            
            elif badAddr_read and line.strip()[0] != "[":
                badAddr.append(line.strip())

    file.close()

    return vlans, ipha, vrf, badAddr

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



def interpretRunningConfig(parse):

    running_SVIs = []
    global_obj = parse.find_objects(r'^hostname')[0]
    hostname = global_obj.re_match_typed(r'^hostname\s+(\S+)', default='__no_hostname__')

    fin_vlanID = []
    fin_vlanNames = []
    print("Interpreting " + hostname + "...")

    for vlan in parse.find_objects('^vlan'): # Find vlan name 
        vlanID = vlan.re_match_typed(r"^vlan\s+(\S.+?)$", result_type=str)
        print("Vlan " + vlanID) # Vlan 300
        fin_vlanID.append(vlanID)
        for child in vlan.children:
            name = child.re_match_typed(r"\sname\s+(\S.+?)$", result_type=str)
            print("name: " + name) # name: computer-lab
            fin_vlanNames.append(name)

    # Display the vlan id and vlan name (L2)
    for i in range(len(fin_vlanID)):
        print("id: " + fin_vlanID[i] + " " + fin_vlanNames[i])

    # Checks for Switch Virtual Interfaces
    for intf_obj in parse.find_objects('^interface Vlan'):  # Find all every parent which starts with interface vlan.
        intf_name = intf_obj.re_match_typed('^interface\s+(\S.+?)$')
        
        # If the current SVI ID Is in the regular vlan ID 
        if intf_name[4:] in fin_vlanID: # If 200 in [100,200]
            print(intf_name[4:])
            print("Found correct SVI in correlation to L2 vlan")
        else:
            print("Current SVI " + intf_name + " do not have a vlan with same ID")

        svi = SVI(hostname, intf_name) # Declaring a SVI object

        stop = False
        # Iterate all children on the interface and check if it is a helper-addresse
        for child in intf_obj.children:
            ip_helper_addr = child.re_match_typed(
            r'ip\shelper-address\s(\d+\.\d+\.\d+\.\d+)', result_type=str, default='__no_match__')
            
            if ip_helper_addr == "__no_match__":  # If the read child is not ip helper-address
                pass
            else:
                # Found a IP Helper Address
                svi.addIPHelperAddr(ip_helper_addr)
            
            # Find VRF
            vrf = child.re_match_typed(
                r'vrf\sforwarding\s+(\S+)', result_type=str, default='__no_vrf__'
                )
            
            if vrf != "__no_vrf__" and stop is False:
                svi.setVRF(vrf)
                stop = True
        
        # Did not find any VRF on the SVI
        if stop is False:
            svi.setVRF("No VRF")
            

        running_SVIs.append(svi)
    print("Done!\n")
    return running_SVIs



def analyseConfigs(req, running):
    
    running_intfName = [] # The name will be stored in the order they are presented in the config
    running_indexes = {}
    j = 0
    running_hostname = ""
    for svi in running:
        running_intfName.append(svi.interfaceName)
        running_indexes[svi.interfaceName] = j
        j += 1
        running_hostname = svi.hostname
        



    for svi in running:
        pass
    # We now have a list of all interfaceNames and the index that they are located at the global SVI object list
    
    # Check if the all the interface vlans are present. 
    # Two loops are required. Check if all SVIs in the template are in the running config
    # And all Vlans are in the template and report to the user the findings of interface Vlans runinng which is not in the template
    
    # [ Hostname, SVI, Missing IPHA, Status]
    # ['Router-1', 'interface Vlan100', '"192.10.1.2, 10.91.3.65", 'Missing IPHA']
    
    #for svi in template:
    #    missing_IPHA = []
    #    temp_missing_svi = []
    #    found_bad_addr = []
        #print("\n")
    #    data = []
    #    data.append(running_hostname)
    #    data.append(svi.interfaceName)
        
        # Check if the Vlan is in the running config:
        # If yes where is it located in the object list, and then check the IP helper addresses
    #    if svi.interfaceName in running_intfName:
     #       k = 0
    #        for name in running_intfName:
    #            if svi.interfaceName == running_intfName[k]:
    #                data.append(running[k].vrf)
    #                
    #                # svi.IPHelperAddr and running[k].IPHelperAddr is the correct interfaces
    #                for helper in  svi.IPHelperAddr:
    #                    if bad_addresses == running[k].IPHelperAddr:
    #                        found_bad_addr.append(helper)
    #                    if helper in running[k].IPHelperAddr:
    #                        for helper2 in running[k].IPHelperAddr:
    #                            if helper == helper2:
    #                                pass

    #                    else:
     #                       missing_IPHA.append(str(helper))
    #                k += 1
    #            else:
    #                k += 1
    #    if svi.interfaceName not in running_intfName:
    #        pass
    #    else:
    #        for svi in running:
    #            for helper in svi.IPHelperAddr:
    #                if helper in bad_addresses:
    #                    found_bad_addr.append(helper)
    #        status = []
    #        if len(missing_IPHA) == 0:
    #            missing_IPHA = "None"
    #        else:
    #            status.append("Missing IPHA")
            
    #        if len(found_bad_addr) == 0:
    #            found_bad_addr = "None"
    #        else:
    #            status.append("Remove Bad Addresse(s)")

    #        if len(status) == 0:
    #            status = "OK"
            
    #        data.append(missing_IPHA)
    #        data.append(found_bad_addr)
    #        data.append(status)

    #        with open('results.csv', 'a', encoding='UTF8', newline='') as f:
    #            writer = csv.writer(f)
    #            writer.writerow(data)
    #            f.close()


def main():


    # Fetch and validate arguments
    req_path, running_path = initArgParser()

    # Start timer
    start = time.perf_counter()

    # Interpret the requirements
    vlan, ipha, vrf, badAddresses = interpretRequirements(req_path)
    req = requirements(vlan, ipha, vrf, badAddresses)

    parser = readConfigFile(running_path)
    running = interpretRunningConfig(parser)

    # Create file
    #header = ['Hostname', 'SVI', 'VRF', 'Missing IPHA', 'Remove Address', 'Status']
    #with open('results.csv', 'w', encoding='UTF8', newline='') as f:
    #    writer = csv.writer(f)

        # write the header
    #    writer.writerow(header)
    #    f.close()
    
    #running_configs = read_list(running_path)


    #for config in running_configs:
        # Parse the running config file
    #    parser = readConfigFile(config)
    #    running_SVIs = interpretRunningConfig(parser)

        # Compare the two configurations
    #    analyseConfigs(req, running_SVIs)
        
    # Stop timer
    #stop = time.perf_counter()

    #print(f"Total runtime: {stop - start:0.4f} seconds")


if __name__ == "__main__":
    main()
