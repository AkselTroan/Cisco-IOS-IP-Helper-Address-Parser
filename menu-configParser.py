from ciscoconfparse import CiscoConfParse
from os import system, name


class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    PURPLE ='\033[0;35m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



def clear():

    # For Windows
    if name == 'nt':
        _ = system('cls')

    # For MacOS and Linux
    else:
        _ = system('clear')


def main_menu():
    # Prints main menu
    clear()
    print(colors.OKGREEN + f'''  ____ _                  ____             __ _         ____                          
 / ___(_)___  ___ ___    / ___|___  _ __  / _(_) __ _  |  _ \ __ _ _ __ ___  ___ _ __ 
| |   | / __|/ __/ _ \  | |   / _ \| '_ \| |_| |/ _` | | |_) / _` | '__/ __|/ _ \ '__|
| |___| \__ \ (_| (_) | | |__| (_) | | | |  _| | (_| | |  __/ (_| | |  \__ \  __/ |   
 \____|_|___/\___\___/   \____\___/|_| |_|_| |_|\__, | |_|   \__,_|_|  |___/\___|_|   
                                                 |___/                                                                    
    ''' + colors.ENDC + colors.OKBLUE + '''
***Some description of what the script does*** 
Found at **Insert GitHub Link**
Written by Aksel Troan

''' + colors.ENDC + 
colors.PURPLE + "[1]" + colors.ENDC + ": Compare two configuration for SVIs and IP Helper Addresses\n" + 
colors.PURPLE + "[2]" + colors.ENDC + ": \n" +
colors.PURPLE + "[3]" + colors.ENDC + ": \n" +
colors.PURPLE + "[4]" + colors.ENDC + ": \n" +  
colors.FAIL + "[q]" + colors.ENDC + ": Quit\n" + colors.ENDC)
def main():
    main_menu()
    input("Waiting for input....")


if __name__ == "__main__":
    main()
