import requests,json,colored,time,shodan
from censys.search import CensysHosts
import zoomeye.sdk as zoomeye
from optparse import *
from colored import stylize
from bs4 import BeautifulSoup
import requests
import operator
import sys
import re
import os
from config_api import shodan_key, zoomeye_key
import pandas
#from pyExploitDb import PyExploitDb 
 
logo = """
 
	 ___________  ______ _           _           
	|_   _| ___ \ |  ___(_)         | |          
	  | | | |_/ / | |_   _ _ __   __| | ___ _ __ 
	  | | |  __/  |  _| | | '_ \ / _` |/ _ \ '__|
	 _| |_| |     | |   | | | | | (_| |  __/ |   
	 \___/\_|     \_|   |_|_| |_|\__,_|\___|_|   
		
	         Powered by @Bl4ckM1rror
                                                                
"""


def Start():
	choose = OptionParser()
	choose.add_option("-s","--search",dest="search",help="Product or OS or Device, etc you want to search for")
	return choose.parse_args()

'''def SetupPyExploitDB():
	print(stylize("[+] SETUP (This may take a long time only the fist time) ",colored.fg('green')))
	pEdb = PyExploitDb()
	pEdb.debug = False
	pEdb.openFile()
	return pEdb'''

def Censys(Search, output):
	print(stylize("--------------------------------------------------------------------", colored.fg("cyan")))
	print(stylize(f"""[+] Search for: {options.search}\n""",colored.fg('cyan')))
	print(stylize(f"""[+] Searching in Censys. . .\n""",colored.fg('cyan')))
	h = CensysHosts()
	results = h.search(Search, pages=-1)
	for result in results:
		if result[0]['ip'] not in output:
			output.append(result[0]['ip'])

def Shodan(Search, output):
	if  shodan_key == "YOUR_SHODAN_API_KEY":
		print(stylize("[-] Insert valid Shodan API Key",colored.fg('red')))
		sys.exit(0)
	print(stylize("--------------------------------------------------------------------", colored.fg("cyan")))
	print(stylize(f"""[+] Search for: {options.search}\n""",colored.fg('cyan')))
	print(stylize(f"""[+] Searching in Shodan. . .\n""",colored.fg('cyan')))
	api = shodan.Shodan(shodan_key)
	try:
		Searchlow = Search.lower()
		results = api.search(Searchlow)
		searchsplit = Searchlow.split(" ")
		for result in results['matches']:
			res = result['data'].lower()
			for word in searchsplit:
				if word in res:
					if len(searchsplit) == 1:
						if result['ip_str'] not in output:
							output.append(result['ip_str'])
					else:
						y = 1
						i = 0
						while y < len(searchsplit):
							str1_occ = [m.start() for m in re.finditer(searchsplit[i], res)]
							str2_occ = [m.start() for m in re.finditer(searchsplit[y], res)]
								
							exitloop = False
							for str1 in str1_occ:
								if exitloop != False:
									break
								
								last_char_srtr1  = str1 + len(searchsplit[i]) -1
								for str2 in str2_occ:
									if (((str2 - last_char_srtr1) > 0) and ((str2 - last_char_srtr1) < 15)):
										if result['ip_str'] is not output:
											output.append(result['ip_str'])
											exitloop = True
											break
							i = i + 1
							y = y + 1
	except shodan.APIError as e:
		print(stylize('Error: {}'.format(e),colored.fg('red')))


def ZoomEye(Search, output):
	if  zoomeye_key == "YOUR_ZOOMEYE_API_KEY":
		print(stylize("[-] Insert valid ZoomEye API Key",colored.fg('red')))
		sys.exit(0)
	zm = zoomeye.ZoomEye()
	zm.api_key = zoomeye_key
	print(styzm.api_keylize("--------------------------------------------------------------------", colored.fg("cyan")))
	print(stylize(f"""[+] Search for: {options.search}\n""",colored.fg('cyan')))
	print(stylize(f"""[+] Searching in Zoomeye. . .\n""",colored.fg('cyan')))
	results = zm.dork_search(Search)
	for result in results:
		if result['ip'] not in output:
			output.append(result['ip'])


#def switch(argument, pEdb):
def switch(argument):
	print(stylize("--------------------------------------------------------------------", colored.fg("white")))
	print(stylize("[?] Which Search Engines do you want use? [?] ", colored.fg("cyan")))
	print(stylize(" s --> Shodan, c --> Censys, z --> ZoomEye, a --> All ", colored.fg("cyan")))
	print(stylize("[!] Please put '+' delimiter if you want to search on multiple Search Engines! [!] ", colored.fg("red")))
	choice = input('Enter your choice --> ')
	while True:
		print(stylize("[?] v -->  Print only vulnerable IP addresses, a --> Print all IP addresses [?] ", colored.fg("cyan")))
		choicecve = input('Enter your choice --> ').lower()
		if (len(choicecve) == 1 and choicecve == 'a' or choicecve == 'v'):
			break
	output = []
	choicelow=choice.lower()
	if len(choicelow) == 1:
		engine = choicelow
	else:
		engine = choicelow.split("+")
	for opt in engine:
		if opt != 's' and opt != 'c' and opt != 'z' and opt != 'a':
			print(stylize("[-] Invalid Search Engine",colored.fg('red')))
			sys.exit(0)
	if len(engine) == 1 and engine == 'a':
		Shodan(argument, output)
		Censys(argument, output)
		ZoomEye(argument, output)
	else:
		for option in engine:
			if option == 's':
				Shodan(argument, output)
			elif option == 'c':
				Censys(argument, output)
			elif option == 'z':
				ZoomEye(argument, output)
			else:
				sys.exit(0)
	try:
		lookupTableVulnIPs = {}
		lookupTableAllIPs = {}
		lookupTableExploit = {}
		cve_list = []
		for host in output:
			url = "https://internetdb.shodan.io/" + host
			res = requests.get(url).json()
			if len(res.keys()) > 1:
				if choicecve == 'v' and len(res[u'vulns']) > 1:
					lookupTableVulnIPs.setdefault(host, res[u'vulns'])
					for cve in res[u'vulns']:
						if cve not in cve_list:
							cve_list.append(cve)
				elif choicecve == 'a':
					lookupTableAllIPs.setdefault(host, res[u'vulns'])
					for cve in res[u'vulns']:
						if cve not in cve_list:
							cve_list.append(cve)
		print(stylize("--------------------------------------------------------------------", colored.fg("white")))
		print(stylize("[+] Search Done [+] ", colored.fg("green")))
		
		change_year = True
		while True:
			if change_year == True:
				print(stylize("[+] All Year CVEs: ", colored.fg("green")))
				year_cve = []
				year_cve_integer = []
				for c in cve_list:
					if c[4:8] not in year_cve:
						year_cve.append(c[4:8])	
				for i in range(0, len(year_cve)):
					year_cve_integer.append(int(year_cve[i]))
				year_cve_integer.sort()
				print(stylize(str(year_cve_integer), colored.fg("cyan")))
					
				while True:
					year2cves = []
					choiceyear = input('Enter Year --> ').lower()
					if choiceyear in year_cve:
						for c in cve_list:
							if c[4:8] == choiceyear:
								if c not in year2cves:
									year2cves.append(c)
						break
					elif choiceyear == 'quit':
						print()
						print("<<< Thanks for using IP-Finder >>>")
						sys.exit(0)	
			#dictionary structure key = CVE, value = Count of IPs affected from CVE i-th
			#initialization dictionary	
			cve2countip = {}
			for cve in year2cves:
					cve2countip.setdefault(cve, 0)
			for cve,countip in cve2countip.items():
				count = 0
				for ip,listacve in lookupTableVulnIPs.items():
					if cve in listacve:
						count = count + 1
				cve2countip[cve] = count
			sorted_d = dict( sorted(cve2countip.items(), key=operator.itemgetter(1),reverse=True))
			print(stylize("[+] All CVEs about selected Year ",  colored.fg("green"))) 
			df = pandas.DataFrame(list(sorted_d.items()),columns = ['CVE ID','Count IP'])
			print(df)
			print(" ")
			while True:
				print(stylize("[?] Enter CVE to search or quit for exit from program [?] ", colored.fg("green")))
				choicesearchsploit = input('Enter CVE --> ').upper()
				if choicesearchsploit in cve_list:
					affected_ip = []	
					#lookupTableVulnIPs contains key = ip, value = all cve for this ip address
					if(choicecve == 'v'):
						for key, value in lookupTableVulnIPs.items():
							for cve in value:
								if cve == choicesearchsploit:
									affected_ip.append(key) 	
					elif(choicecve == 'a'):
						for key, value in lookupTableAllIPs.items():
							for cve in value:
								if cve == choicesearchsploit:
									affected_ip.append(key)  
					choicefile = input('Do you want to save targets in a file? Y/N --> ').upper()
					if choicefile == 'Y':
						filename = choicesearchsploit + '.txt'
						with open(filename, 'w') as f:
							for ip in affected_ip:
								f.write(ip)
								f.write('\n')
						f.close()	
					else:	
						print(stylize("--------------------------------------------------------------------", colored.fg("white")))
						print(stylize("[+] Search Done [+] ", colored.fg("green")))
						print(stylize("[+] all IPs affected: ", colored.fg("cyan")))
						print(affected_ip)	
					print(stylize("--------------------------------------------------------------------", colored.fg("white")))
					print(stylize("[+] Please wait, searching for Metasploit module. . . ", colored.fg("green")))
					os.system("msfconsole -q -x 'search %s; exit;' -o suggested_exploit.txt"%(choicesearchsploit))
					filepath = 'suggested_exploit.txt'
					f1 = open(filepath, 'r')
					lines = f1.readlines()
					if lines[0] != '[-] No results from search\n':
						for row in lines:
							if "Name" in row or "exploit" in row or "auxiliary" in row:
								print(row)
					else:
						print(stylize("[-] No results found", colored.fg("red")))
						#print(stylize("[+] Please wait, searching module in Exploit-DB repository. . . ", colored.fg("green")))
						#print(pEdb.searchCve(choicesearchsploit))
					os.system("rm -rf suggested_exploit.txt")
					choicechangeyear = input('Do you want change year? Y/N --> ').lower()
					if choicechangeyear == 'y':
						change_year = True
					else:
						change_year = False
					break
				elif choicesearchsploit == 'QUIT':
					print()
					print("<<< Thanks for using IP-Finder >>>")
					sys.exit(0)
	except Exception as e:
		print(e)
		print(stylize("""[-] Please specify Search.
		Example: python3 IP-Finder.py Device type or version""", colored.fg('cyan')))
		
		
print(stylize(logo,colored.fg('cyan')))
(options, arguments) = Start()
if len(sys.argv) == 1:
		print(stylize("""[-] Please specify Search. Example: python3 IP-Finder.py Device type or version""", colored.fg('cyan')))
		sys.exit(0)
switch(options.search)
#pEdb = SetupPyExploitDB()
#switch(options.search, pEdb)
