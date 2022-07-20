import pandas as pd

def remove_bad_addr(hostname, interface, bad_addr):
    '''
    Should be called when all bad addresses for a router has been 
    assembled. Only run this function once per router
    '''
    
    config = []
    print("\n")
    config.append("Run this command on host: " + hostname)
    if len(interface) == 1:

        config.append("!")
        config.append("interface " + interface[0])
        for addr in bad_addr:
            config.append("no ip helper-address " + addr)

        config.append("!")
        for line in config:
            print(line)
    else:
        for intf in interface:
            config.append("!")
            config.append("interface " + intf)
            for addr in bad_addr:
                config.append("no ip helper-address " + addr)

            config.append("!")
            for line in config:
                print(line)


def generateNewConfig():
    df = pd.read_excel("./test.xlsx", index_col=0)

    print("Generate new config")

    bad_add = {"Hostname": [],
            "Interface": [],
            "bad_addr": []}

    
    # iterate through each row and select
    for ind in df.index:
        host = ""
        interface = []
        addr = []
        #print(df['Hostname'][ind], df['Status'][ind])
        if "GigabitEthernet" in df['Interface'][ind]:
            #print("Found GigabitEthernet interface")
            pass
            #print(df['Hostname'][ind], df['Interface'][ind], df['VRF'][ind], df['IPHA'][ind], df['Status'][ind])
        if df["Status"][ind] == "Bad Address":
            # Run gen config for this interface
            #print("Bad Address Found!")
            host = df['Hostname'][ind]
            interface.append(df['Interface'][ind])
            addr.append(df['IPHA'][ind])
            bad_add['Hostname'] = host
            bad_add['Interface'] = interface
            bad_add['bad_addr'] = addr
            remove_bad_addr(bad_add['Hostname'], bad_add['Interface'], bad_add['bad_addr'])