from netaddr import *
from init.svi import SVI

def interpretRunningConfig(parse, bad_addr):
    a_hostname = []
    a_svi = []
    a_vrf = []
    a_ipha = []
    a_status = []
    global_obj = parse.find_objects(r'^hostname')[0]
    hostname = global_obj.re_match_typed(r'^hostname\s+(\S+)', default='__no_hostname__')

    for intf_obj in parse.find_objects('^interface\s.+'):  # Find all every parent which starts with interface
        intf_name = intf_obj.re_match_typed('^interface\s+(\S.+?)$')
        svi = SVI(hostname, intf_name) # Declaring a SVI object

        stop = False
        # Iterate all children on the interface and check if it is a helper-addresse
        for child in intf_obj.children:
            ip_helper_addr = child.re_match_typed(
            'ip\shelper-address\s(.+)', result_type=str, default='__no_match__')

            if ip_helper_addr == "__no_match__":  # If the read child is not ip helper-address
                app = False
            else:
                app = True
                # Found a IP Helper Address
                svi.addIPHelperAddr(ip_helper_addr)
            
            # Find VRF
            vrf = child.re_match_typed(
                r'vrf\sforwarding\s+(\S+)', result_type=str, default='__no_vrf__'
                )
            if vrf != "__no_vrf__" and stop is False:
                stop = True
                f_vrf = vrf

            if app == True:
                a_hostname.append(hostname)
                a_svi.append(intf_name)
                a_ipha.append(ip_helper_addr)
                if stop is False:
                    f_vrf = vrf
                    a_vrf.append("No VRF")
                else:
                    a_vrf.append(f_vrf)
                if ip_helper_addr in bad_addr:
                    a_status.append("Bad Address")
                else:
                    a_status.append("Good Address")

    return a_hostname, a_svi, a_vrf, a_ipha, a_status


def find_big_networks(parse):
    '''
    Find all networks with mask which has not /32-26
    '''

    a_hostname = []
    a_intf = []
    a_desc = []
    a_network = []

    global_obj = parse.find_objects(r'^hostname')[0]
    hostname = global_obj.re_match_typed(r'^hostname\s+(\S+)', default='__no_hostname__')
    
    banned_subnet = ["/32", "/31", "/30", "/29", "/28", "/27", "/26"]
    
    for intf_obj in parse.find_objects('^interface\s.+'):  # Find all every parent which starts with interface
        intf_name = intf_obj.re_match_typed('^interface\s+(\S.+?)$')
        no_IP = True
        no_desc = True
        for child in intf_obj.children:
            desc = child.re_match_typed(
                'description\s(.+)', result_type=str, default="No description"
            )
            if desc != "No description":
                print("Description: " + desc)
                no_desc = False
            else:
                pass

            ip_addr = child.re_match_typed(
                'ip\saddress\s(.+)', result_type=str, default="Found no IP"
            )
            if ip_addr != "Found no IP":
                tmp_ip = ip_addr.split(" ")
                subnet_mask = "/" + str(IPAddress(tmp_ip[1]).netmask_bits())
                if subnet_mask in banned_subnet:
                    no_IP = False
                else:
                    ip = str(tmp_ip[0]) + subnet_mask
                    #print(hostname + " " + intf_name + ": " + ip)
                    no_IP = False

        print(desc)
        if no_IP:
            a_hostname.append(hostname)
            a_intf.append(intf_name)
            a_desc.append(desc)
            a_network.append("None")
        else:
            a_hostname.append(hostname)
            a_intf.append(intf_name)
            a_desc.append(desc)
            #a_network.append(ip)
        if no_IP:
            print(hostname + "\nInterface: " + intf_name + "\nDescription: " + desc + "\nNetwork: None")

        #print(hostname + "\nInterface: " + intf_name + "\nDescription: " + desc + "\nNetwork: " + ip)
        print("\n")