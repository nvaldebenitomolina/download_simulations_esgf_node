 #!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd 
import numpy as np
import re
import operator
import os 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from selenium.webdriver.common.action_chains import ActionChains
import configparser
import sys 
from toripchanger import TorIpChanger
import requests
import warnings

warnings.simplefilter("ignore")

#Busqueda de ip request compatible
def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies

def contador():
  numero = 0
  while True:
    numero += 1
    yield numero

time.sleep(3)
chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('headless')
chrome_options.add_argument("--window-size=1920,1080");
chrome_options.add_argument("--start-maximized");
chrome_options.add_argument("--headless");
chrome_options.add_experimental_option('prefs', {'safebrowsing.enabled': True}); 
chrome_options.add_argument('--safebrowsing-disable-download-protection')
driver = webdriver.Chrome(executable_path="/usr/lib64/chromium-browser/chromedriver",chrome_options = chrome_options)
#driver = webdriver.Chrome(executable_path="/usr/lib64/chromium-browser/chromedriver", chrome_options = chrome_options)
config = configparser.ConfigParser()
config.read(sys.argv[1])
#open webdriver

driver.get("https://esgf-node.llnl.gov/login/?next=http://esgf-node.llnl.gov/search/cmip6/")
driver.maximize_window()
#user and password
usuario1=os.environ["usuario_wget1"]
usuario2=os.environ["usuario_wget2"]
password=os.environ["password_wget"] 

time.sleep(4)
driver.find_element_by_xpath('//*[@id="openid_identifier"]').send_keys(usuario1)
driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[5]/div/div/form/div[1]/table/tbody/tr[2]/td[3]/input').click()
time.sleep(6)
driver.find_element_by_xpath('//*[@id="username"]').send_keys(usuario2)
driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)
driver.find_element_by_xpath('//*[@id="loginCommand_ids"]/table/tbody/tr[2]/td[2]/input[2]').click()


#select simulation
time.sleep(5)
driver.find_element_by_xpath('//*[@id="search-form"]/div[1]/div/div[1]/div/div[3]/a').click()
time.sleep(1)
driver.find_element_by_name(config['general']['tipo']).click()
#select experiment
driver.find_element_by_xpath('//*[@id="search-form"]/div[1]/div/div[9]/div/div[3]/a').click()
time.sleep(1)
driver.find_element_by_name(config['general']['experimento']).click()
#select variable'
driver.find_element_by_xpath('//*[@id="search-form"]/div[1]/div/div[16]/div/div[3]/a').click()
time.sleep(1)
driver.find_element_by_name(config['general']['variable']).click()
#select frequency
driver.find_element_by_xpath('//*[@id="search-form"]/div[1]/div/div[14]/div/div[3]/a').click()
time.sleep(1)
driver.find_element_by_name(config['general']['frecuencia']).click()

#search button
time.sleep(1)
driver.find_element_by_xpath('//*[@id="search-form"]/div[2]/table/tbody/tr[1]/td[2]/div/table/tbody/tr/td/input[1]').click()


time.sleep(2)
driver.find_element_by_xpath('//*[@id="search-form"]/div[1]/div/div[18]/div/div[3]/a').click()
time.sleep(2)
#review number of files
results=driver.find_element_by_xpath('//*[@id="search-form"]/div[2]/div[4]').text.split('\n')[0]
print(results)
#number of nodos 
nodos=driver.find_elements_by_xpath('//*[@id="yuievtautoid-0"]/div/div/li')

cuenta = contador()
total_wget=[]
for n in range(1,len(nodos)+1):
	print('***********************')
	print(f'NODO {n}')
	time.sleep(2)
	nodos=driver.find_elements_by_xpath('//*[@id="yuievtautoid-0"]/div/div/li')
	print(f'cantidad de nodos:{len(nodos)}')

	#nodo para buscar informacion
	nodo_search=driver.find_element_by_xpath('//*[@id="search-form"]/div[1]/div/div[18]/div/div[2]/div/div/li['+str(n)+']/input')
	nodo_search.click()
	
	
	driver.find_element_by_xpath('//*[@id="search-form"]/div[2]/table/tbody/tr[1]/td[2]/div/table/tbody/tr/td/input[1]').click()
	print('nodo: '+driver.find_element_by_xpath('//*[@id="search-form"]/div[2]/p[1]/a[10]').text+'')
	#select 100 

	driver.find_element_by_xpath('//*[@id="limit"]/option[4]').click()
	time.sleep(2)
	driver.find_element_by_xpath('//*[@id="search-form"]/div[2]/table/tbody/tr[1]/td[2]/div/table/tbody/tr/td/input[1]').click()
	results=driver.find_element_by_xpath('//*[@id="search-form"]/div[2]/div[4]').text.split('\n')[0].split(': ')[1]
	print(f'cantidad de wget:{results}')
	

	total=[]

	for m in range(1,int(results)+1):
		number=driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[5]/div[1]/form/div[2]/div[5]/table/tbody/tr['+str(m)+']/td[2]/div[1]').text
		total.append(int(number.split('\n')[3].split(': ')[1]))

	print(f'total de archivos: {sum(total)}')
	
	if sum(total) > 1000:
		print('total de archivos mayor a 1000')
		driver.find_element_by_xpath('//*[@id="limit"]/option[1]').click()
		time.sleep(2)
		driver.find_element_by_xpath('//*[@id="search-form"]/div[2]/table/tbody/tr[1]/td[2]/div/table/tbody/tr/td/input[1]').click()
		search=driver.find_elements_by_xpath('//*[@id="search-form"]/div[2]/div[4]/a')
		
		value=len(search)-5
		for j in range(1,value+1):
			driver.find_element_by_xpath(".//*[text()='Next >>']")
			
			click_here = driver.find_element_by_xpath(".//*[text()='Add all displayed results to Data Cart']") # try different xpaths.
			click_here.location_once_scrolled_into_view # As the element needs scroll down
			click_here.click()

			driver.find_element_by_xpath('//*[@id="top_subnav_right"]/a[2]').click()
			time.sleep(2)
			driver.find_element_by_xpath('//*[@id="datacart-checkbox"]').click()
			time.sleep(1)

			driver.find_element_by_xpath('//*[@id="datacart-table"]/tbody/tr[1]/td/strong[2]/a').click()
			time.sleep(1)
			driver.find_element_by_xpath('//*[@id="wget-scripts"]/div[2]/a').click()

			print('downloading')
			total_wget.append(next(cuenta))

			time.sleep(1)
			driver.find_element_by_xpath('//*[@id="datacart-table"]/tbody/tr[3]/td[3]/a').click()
			time.sleep(1)
			driver.find_element_by_xpath('//*[@id="yui-gen0-button"]').click()
			time.sleep(1)
			driver.find_element_by_xpath('//*[@id="top_subnav_right"]/a[1]').click()
			time.sleep(1)
			try:
				driver.find_element_by_xpath('//*[@id="search-form"]/div[2]/div[4]/a[4]')
				print(f'Downloading next {j+1}')
				driver.find_element_by_xpath(".//*[text()='Next >>']")
				click_here = driver.find_element_by_xpath(".//*[text()='Add all displayed results to Data Cart']") # try different xpaths.
				click_here.location_once_scrolled_into_view # As the element needs scroll down
				click_here.click()

				driver.find_element_by_xpath('//*[@id="top_subnav_right"]/a[2]').click()
				time.sleep(2)
				driver.find_element_by_xpath('//*[@id="datacart-checkbox"]').click()
				time.sleep(1)

				driver.find_element_by_xpath('//*[@id="datacart-table"]/tbody/tr[1]/td/strong[2]/a').click()
				time.sleep(1)
				driver.find_element_by_xpath('//*[@id="wget-scripts"]/div[2]/a').click()

				print('downloading')
				total_wget.append(next(cuenta))

				time.sleep(1)
				driver.find_element_by_xpath('//*[@id="datacart-table"]/tbody/tr[3]/td[3]/a').click()
				time.sleep(1)
				driver.find_element_by_xpath('//*[@id="yui-gen0-button"]').click()
				time.sleep(1)
				driver.find_element_by_xpath('//*[@id="top_subnav_right"]/a[1]').click()
				time.sleep(1)
			except:
				print('Finished download, files > 1000')


	else:
		click_here = driver.find_element_by_xpath(".//*[text()='Add all displayed results to Data Cart']") # try different xpaths.
		click_here.location_once_scrolled_into_view # As the element needs scroll down
		click_here.click()

		driver.find_element_by_xpath('//*[@id="top_subnav_right"]/a[2]').click()
		time.sleep(2)
		driver.find_element_by_xpath('//*[@id="datacart-checkbox"]').click()
		time.sleep(1)

		driver.find_element_by_xpath('//*[@id="datacart-table"]/tbody/tr[1]/td/strong[2]/a').click()
		time.sleep(3)
		driver.find_element_by_xpath('//*[@id="wget-scripts"]/div[2]/a').click()

		print('downloading')
		total_wget.append(next(cuenta))

		time.sleep(1)
		driver.find_element_by_xpath('//*[@id="datacart-table"]/tbody/tr[3]/td[3]/a').click()
		time.sleep(1)
		driver.find_element_by_xpath('//*[@id="yui-gen0-button"]').click()
		time.sleep(1)
		driver.find_element_by_xpath('//*[@id="top_subnav_right"]/a[1]').click()
		time.sleep(1)

	delete=driver.find_element_by_xpath('//*[@id="search-form"]/div[2]/p[1]/a[9]')


	delete.click()
	time.sleep(2)
	#driver.find_element_by_xpath('//*[@id="search-form"]/div[2]/table/tbody/tr[1]/td[2]/div/table/tbody/tr/td/input[1]').click()
	driver.find_element_by_xpath('//*[@id="search-form"]/div[1]/div/div[18]/div/div[3]/a').click()

os.system(f"mkdir {config['general']['tipo']}_{config['general']['experimento']}_{config['general']['frecuencia']}_{config['general']['variable']}")
os.system(f"mv *.sh {config['general']['tipo']}_{config['general']['experimento']}_{config['general']['frecuencia']}_{config['general']['variable']}")

print(total_wget[-1])