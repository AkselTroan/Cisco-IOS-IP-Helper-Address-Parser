
from ciscoconfparse import CiscoConfParse
import time, sys, os, csv

from pkg_resources import working_set


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
        self.hostname = hostname # String
        self.vlanIDs = vlanIDs # List of integers
        self.vlanNames = vlanNames # List of strings
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
            pass
        
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
                line = line.strip()
                line = line.split(":")
                addr_list = line[1].split(",")
                line[1] = addr_list
                ipha.append(line)
        
            elif vrf_read and line.strip()[0] != "[":
                line = line.strip()
                line = line.split(":")
                vrf.append(line)
            
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
        # vlanID: 300
        fin_vlanID.append(vlanID)
        for child in vlan.children:
            name = child.re_match_typed(r"\sname\s+(\S.+?)$", result_type=str)
            # name: computer-lab
            fin_vlanNames.append(name)

    # Display the vlan id and vlan name (L2)
    #for i in range(len(fin_vlanID)):
    #    print("id: " + fin_vlanID[i] + " " + fin_vlanNames[i])

    # Checks for Switch Virtual Interfaces
    for intf_obj in parse.find_objects('^interface Vlan'):  # Find all every parent which starts with interface vlan.
        intf_name = intf_obj.re_match_typed('^interface\s+(\S.+?)$')
        
        # If the current SVI ID Is in the regular vlan ID 
        if intf_name[4:] not in fin_vlanID: # If 200 in [100,200]
            print("Current SVI " + intf_name + " do not have a vlan with same ID. Skipping...")
            # Should be reported!
        else:
            # Found correct SVI in correlation to L2 vlan
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
                    for i in range(len(fin_vlanID)):
                        if intf_name[4:] == fin_vlanID[i]:
                            current_vlan = fin_vlanNames[i]
                    final = []
                    final.append(current_vlan)
                    final.append(vrf)
                    svi.setVRF(final)
                    stop = True
            
            # Did not find any VRF on the SVI
            if stop is False:
                svi.setVRF("No VRF")
                

            running_SVIs.append(svi)

    # Make a new host object (Remember to add the SVIs to the host along with hostname and vlans)
    host = Host(hostname, fin_vlanID, fin_vlanNames, running_SVIs)
    print("Done!\n")
    return host



def analyseConfig(req, host):
    
    missing_vlan_names = []
    
    # Checking for missing vlan names
    for name in req.vlans:
        if name not in host.vlanNames:
            print("Missing VLAN: " + name)
            missing_vlan_names.append(name)



    wrong_vrf = []
    correct_vrf = []
    wrong_vlan = []
    correct_vlan = []
    # Check VRF
    for vrf in req.vrfs:
        for svi in host.SVIs:
            if vrf[0] != svi.vrf[0]:
                #print("Could not find correct Vlan" + " " + str(vrf[0]) + " " + str(svi.vrf[0]))
                wrong_vlan.append(vrf[0])
            else:
                #print("Found Correct Vlan: "  + str(vrf[0]) + " " + str(svi.vrf[0]))
                correct_vlan.append(vrf[0])
    
            if vrf[1] != svi.vrf[1]:
                #print("Could not find correct VRF" + " " + str(vrf[1]) + " " + str(svi.vrf[1]))
                wrong_vrf.append(svi.vrf[1])
            else:
                #print("Found Correct VRF: "  + str(vrf[1]) + " " + str(svi.vrf[1]))
                correct_vrf.append(vrf[1])            

    for vrf in wrong_vrf:
        for cvrf in correct_vrf:

            if vrf == cvrf:
            # remove vrf from the wrong vrf list
                try:
                    del wrong_vrf[wrong_vrf.index(vrf)]
                except:
                    pass
    
    # Remove duplicates
    tmp = []
    [tmp.append(x) for x in wrong_vrf if x not in tmp]
    wrong_vrf = tmp
    
    print("")
    print("Misconfigured correlation between vlans and vrfs") 
    for i in range(len(wrong_vrf)):
        print("Vlan " + wrong_vlan[i] + " Has wrong vrf (" + wrong_vrf[i] + ")")

    # Check IP Helper Addresses
    for vlan in correct_vlan:
        for svi in host.SVIs:
            for ipha in svi.IPHelperAddr:
                for i in range(len(req.ipha[1])):
                    ipha2 = req.ipha[i][1]
                    for ip in ipha2:
                        #print(vlan)
                        #print(req.vrfs[0][0])
                        if vlan == req.ipha[i][0]:
                            print("ipha2: " + str(ipha2))
                            print("ipha: " + ipha)
                            if ip in ipha:
                                print("Success")
                                print("Found IPHA: " + ip)
                            else:
                                print("Missing IPHA: " + ip)
        

    # Check bad-addresses

    for ba in req.badAddresses:
        for svi in host.SVIs:

            if ba in svi.IPHelperAddr:
                print("Found bad address: " + ba)
                # Should be reported

    # We now have a list of all interfaceNames and the index that they are located at the global SVI object list
    
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

    running_configs = read_list(running_path)
    for config in running_configs:

        parser = readConfigFile(config)
        host = interpretRunningConfig(parser)
        analyseConfig(req, host)
        # How do we find the correlation between vlans and SVIs.
        # We know that they can existst, however how do we make the link between them. 

    
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
