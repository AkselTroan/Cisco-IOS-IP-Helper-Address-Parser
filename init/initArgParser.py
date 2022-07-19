import sys, os


def initArgParser():

    if not os.path.isfile(sys.argv[1]):
        print(f'{sys.argv[1]} does not exist')
        sys.exit()


    elif len(sys.argv) != 2:
        print("usage: configParser.py <running-config/List of running-config files>")
        sys.exit()
    
    elif not os.path.isfile(sys.argv[1]):
        print("Submitted file does not exist")
        sys.exit()

    else:
        running = sys.argv[1]
    
    return ("./" + running)
