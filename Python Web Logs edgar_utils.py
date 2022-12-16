# Ameya Baxi (some collaboration with lab team members)
# COMP SCI 320: Data Science Programming II, Fall 2022
# Project 5: EDGAR Web Logs

# analyzing data from EDGAR web logs (database of reports from public companies to Securities and Exchange Commission)
# project instructions: https://github.com/cs320-wisc/f22/tree/main/p5

import netaddr, pandas as pd, re
from bisect import bisect
from zipfile import ZipFile

with ZipFile("server_log.zip", "r") as f:
    file = f.filename
    rows_csv = pd.read_csv(file)
    
ip_locs = pd.read_csv("ip2location.csv") # read csv with locations of IP addresses as pandas DataFrame

# function to find the region of an IP address
def lookup_region(ip):
    if type(ip) != str: # check that IP address is type string
        return "bad input"
    ip = re.sub(r"[^\d.]", "0", ip)
    ip = int(netaddr.IPAddress(ip))
    idx = bisect(ip_locs["low"], ip) - 1
    region = ip_locs.iloc[idx]["region"]
    return region


# extract information from html
class Filing:
    def __init__(self, html):
        self.dates = []
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", html)
        for date in dates:
            if date[:2] == "19" or date[:2] == "20":
                self.dates.append(date)
        self.sic = re.findall(r"SIC=(\d+)", html)
        if self.sic == []:
            self.sic = None
        else:
            self.sic = int(self.sic[0])
        self.addresses = []
        addresses = []
        for address in re.findall(r"<div class=\"mailer\">([\s\S]+?)</div>", html): #([\s\S]+?) #(.+?)
            lines = []
            for line in re.findall(r"<span class=\"mailerAddress\">([\s\S]+?)\s*</span>", address): #([\s\S]+?)\s*
                lines.append(line)
            addresses.append("\n".join(lines)) # \n
        for address in addresses:
            if address != "":
                self.addresses.append(address)
            
    def state(self):
        for address in self.addresses:
            state = re.findall(r"[A-Z]{2}\s\d{5}", address)
            if state != []:
                return state[0][:2]
        return None