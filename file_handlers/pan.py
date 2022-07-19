import pandas as pd

def coll():
    return['Hostname', 'SVI', 'VRF', 'IPHA', 'Status']
def test(hostname, svi ,vrf, ipha, status):


    di = {"Hostname": hostname,
            "SVI": svi,
            "VRF": vrf,
            "IPHA": ipha,
            "Status": status}

    test = pd.DataFrame(di)

    print(test)

