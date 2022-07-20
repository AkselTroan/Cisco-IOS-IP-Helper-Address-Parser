from init.svi import SVI

def interpretRunningConfig(parse, bad_addr):
    a_hostname = []
    a_svi = []
    a_vrf = []
    a_ipha = []
    a_status = []
    global_obj = parse.find_objects(r'^hostname')[0]
    hostname = global_obj.re_match_typed(r'^hostname\s+(\S+)', default='__no_hostname__')

    for intf_obj in parse.find_objects('^interface\s.+'):  # Find all every parent which starts with interface .
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

