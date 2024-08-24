import re, os, sys, time
from os import path
from random import randint
import configparser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from subprocess import CREATE_NO_WINDOW

class hortifruti:
    def __init__(self) -> None:
        self.web_driver = None
        self.file_path = path.dirname(path.abspath(__file__))

    def start_site(self):
        '''
        Inicializa o chrome driver e inicializa a pagina inicial do mercado horti fruti.
        '''
        self.web_driver = None
        try:
            options = webdriver.ChromeOptions()
            #options.add_argument('--ignore-ssl-errors')
            #options.add_argument('--ignore-certificate-errors')
            #options.add_argument("--log-level=3")
            options.add_argument("--disable-notifications")
            options.add_argument('--disable-infobars')
            options.add_experimental_option('excludeSwitches', ['load-extension','enable-automation','disable-popup-blocking'])
            ## faz com que o browser nao abra durante o processo
            #options.add_argument("--headless") 
            ## caminho para o webdriver
            drive_file = path.join(self.file_path,'chromedriver.exe')
            service = webdriver.ChromeService(executable_path=drive_file)
            service.creationflags = CREATE_NO_WINDOW
            self.web_driver = webdriver.Chrome(service=service,options=options)
            zonasul_url = "https://hortifruti.com.br/"
            self.web_driver.get(zonasul_url)
            assert "Supermercados horti fruti" in self.web_driver.title
            #Estabelece o tempo de espera neste drive
            wait = WebDriverWait(self.web_driver, 15)
            #aguarda ate o elemento com certo ID ser clicavel
            wait.until(EC.presence_of_element_located((By.ID, 'search')))

        except AssertionError  as asser:
            print ("[ERRO] - A pagina encontrada nao e do mercado horti fruti. Por favor, verifique se a pagina ["+zonasul_url+"] esta acessivel ")
            os.system('pause') 
            #raise Exception("A pagina encontrada nao e do mercado horti fruti. Por favor, verifique se a pagina ["+zonasul_url+"] esta acessivel ")
            #sys.exit()
        except Exception as e:
            #exc_type, exc_value, exc_tb = sys.exc_info()
            #self.ont_log.exception_handler(exc_type, exc_value, exc_tb)
            print(e.__cause__)
            os.system('pause') 
            #raise Exception(exc_value)
            #sys.exit() 

    def busca_produto(self, produto):
        '''
        Inicializa o chrome driver e inicializa a pagina inicial  de busca de um produto
        no mercado horti fruti.
        '''
        self.web_driver = None
        try:
            options = webdriver.ChromeOptions()
            #options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            #options.add_argument('--disable-dev-shm-usage')
            #options.add_argument('--start-maximized')
            #options.add_argument('--user-agent=Mozilla/5.0 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36') # TROCANDO O USER-AGENT Mozilla/5.0 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36
            options.add_argument('--ignore-certificate-errors')
            #options.add_argument('--window-size=1024x768')
            #wd = webdriver.Chrome('chromedriver',options=options, service_args=['--verbose', '--log-path=/tmp/chromedriver.log'])
            options.add_argument('--ignore-ssl-errors')
            #options.add_argument('--ignore-certificate-errors')
            options.add_argument("--log-level=3")
            options.add_argument("--disable-notifications")
            options.add_argument('--disable-infobars')
            #options.add_experimental_option('excludeSwitches', ['load-extension','enable-automation','disable-popup-blocking'])
            ## faz com que o browser nao abra durante o processo
            options.add_argument("--headless") 
            # tratamento do produto
            prod_busca = produto.replace(' ','+')
            ## caminho para o webdriver
            drive_file = path.join(self.file_path,'chromedriver.exe')
            service = webdriver.ChromeService(executable_path=drive_file)
            service.creationflags = CREATE_NO_WINDOW
            self.web_driver = webdriver.Chrome(service=service,options=options)
            self.web_driver.delete_all_cookies()
            hortifruti_url = "https://hortifruti.com.br/catalogsearch/result/?q="+prod_busca
            self.web_driver.get(hortifruti_url)
            wait = WebDriverWait(self.web_driver, 10)
            # Verificando se ter msgs
            #try:
            #    wait.until(EC.presence_of_element_located((By.XPATH, "//form[@class='vex-dialog-form']")))
            #    aceitar_button = self.web_driver.find_element(by=By.XPATH, value='//button[@class="accept-btn vex-dialog-button vex-first"]')
            #    aceitar_button.click()
            #except:
            #    print ("Sem msgs no form.")
            # verificando se tem alertas
            try:
                wait_alert = WebDriverWait(self.web_driver, timeout=5)
                wait_alert.until(EC.alert_is_present())
                alert = self.web_driver.switch_to.alert
                text = alert.text
                alert.accept()
                self.web_driver.switch_to.default_content()
            except:
                print ("Sem alertas.")

            return self.web_driver.page_source

        except AssertionError  as asser:
            print ("[ERRO] - A pagina encontrada nao e do mercado horti fruti. Por favor, verifique se a pagina ["+hortifruti_url+"] esta acessivel ")
            os.system('pause') 
            #raise Exception("A pagina encontrada nao e do mercado horti fruti. Por favor, verifique se a pagina ["+hortifruti_url+"] esta acessivel ")
            #sys.exit()
        except Exception as e:
            #exc_type, exc_value, exc_tb = sys.exc_info()
            #self.ont_log.exception_handler(exc_type, exc_value, exc_tb)
            print(e.__cause__)
            os.system('pause') 
            #raise Exception(exc_value)
            #sys.exit() 
        finally:
            if self.web_driver:
                self.web_driver.close()
    
    def recupera_produtos(self, page_source):
        produtos = {}
        soup = BeautifulSoup(page_source,'html.parser')
        nome_itens = soup.find_all('li',{"class":"item product product-item"})
        for it in nome_itens:
            nm = it.find('a',{"class":"product-item-link"})
            if nm != None:
                print (nm.text.strip())
                preco = it.find_all('span',{"class":"price"})
                if preco != None and preco != '':
                    produtos[nm.text.strip()] = preco[0].text
                    print(preco[0].text)
                else:
                    produtos[nm.text.strip()] = 'INDISPONIVEL'

        return produtos