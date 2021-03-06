# Introduction

Hunts IP Helper addresses on Switch Virtual Interfaces and compare them to a template configuration which contains desired configuration and addresses.

The software comes in different forms:

* Run a single comparison between two configuration

* Run comparison on multiple files at once (multiple files compared to one template configuration). 

It will display the data in form of a csv file. All the missing IP Helper Addresses in addition to missing Switch Virtual Interfaces. 


# Usage

### Bad addresses
To add bad addresses, edit the bad-addresses file with one address each line. 

### Single comparison
```
python3 configParser.py <template-config> <running-config>
```


### Compare multiple configs and generate a CSV report
```
python3 configParser.py <template-config> <list of configs pathways>
```

# Example Output:

|Hostname|	       SVI	       |                   Missing IPHA	            |Remove Address|	Status|
|--------|---------------------|--------------------------------------------|--------------|----------|
|router-1|interface Vlan500|"['192.10.44.5', '50.50.50.50']"|None|['Missing IPHA']|
|router-1|interface Vlan600|"['16.16.16.11', '20.20.20.200']"|None|['Missing IPHA']|
|router-2|interface Vlan600|"['192.10.42.27', '16.16.16.11', '20.20.20.200']"|None|['Missing IPHA']|
|router-3|interface Vlan500|"['20.20.20.20', '192.10.44.5', '50.50.50.50']"|None|['Missing IPHA']|
|router-3|interface Vlan600|"['16.16.16.11', '20.20.20.200']"|None|['Missing IPHA']|
|router-4|interface Vlan600|"['16.16.16.11', '20.20.20.200']"|['101.101.101.101']|"['Missing IPHA', 'Remove Bad Addresse(s)']"|
|router-5|interface Vlan500|"['10.10.10.10', '192.10.44.5', '50.50.50.50']"|None|['Missing IPHA']|
|router-6|interface Vlan500|None|None|OK|
|router-6|interface Vlan600|None|None|OK|
