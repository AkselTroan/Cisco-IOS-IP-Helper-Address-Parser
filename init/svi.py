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
