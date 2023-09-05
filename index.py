# Importando as bibliotecas
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from openpyxl.workbook import Workbook

# Configurando as opções do Chrome
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Descomente esta linha se desejar executar o Chrome em modo headless

# Instalando o driver do Chrome e obtendo o caminho do executável
chrome_driver_path = ChromeDriverManager().install()

# Passando o caminho do executável do driver e as opções para o construtor
driver = webdriver.Chrome(options=options)

# Lista para armazenar os links dos produtos
links_produto = []

for i in range(1, 83):
    url = f"https://www.guiatelefone.com/search?button=&city_id=&page={i}&what=COMERCIOS&where=S%C3%A3o+Jos%C3%A9+dos+Pinhais%2C+PR"
    
    driver.get(url)
    
    print(f"-- Acessando o index: {i}")
    
    sleep(3)
    
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    h2_elements = soup.find_all('h2')
    
    for h2 in h2_elements:
        link = h2.find('a')['href']
        link_produtos = f'https://www.guiatelefone.com{link}'
        print(link_produtos)
        links_produto.append(link_produtos)
        print(f'Total de link: {len(links_produto)}')
        
# Crie um DataFrame com os links dos produtos
#df_links = pd.DataFrame(links_produto, columns=["Link"])

# Salve os links dos produtos em um arquivo Excel
#df_links.to_excel("links_produtos.xlsx", index=False)

# Carregue os links dos produtos a partir do arquivo Excel
df_links = pd.read_excel("links_produtos.xlsx")

# Lista para armazenar todas as informações coletadas
todas_informacoes = []

count = 0

for index, row in df_links.iterrows():
    
    link_produtos = row["Link"]
    
    print(f'Acessando a url do produto: {link_produtos}')
    
    driver.get(link_produtos)
    sleep(1)
    
    try:
        nome_empresa = driver.find_element(By.CSS_SELECTOR, "body > main > section > div > div.pt-3.pb-5.mb-6.border-b.border-gray-200 > h1").text.strip()
        endereco = driver.find_element(By.CSS_SELECTOR, "body > main > section > div > div.md\:flex > div.min-w-0.grow > div.space-y-6 > div:nth-child(1) > div:nth-child(2) > p").text.strip()
        telefone = driver.find_element(By.CSS_SELECTOR, "body > main > section > div > div.md\:flex > div.min-w-0.grow > div.space-y-6 > div:nth-child(1) > div:nth-child(3) > ul > li > span > a").text.strip()
        
        print(f"ID: {count}|Empresa: {nome_empresa} | Endereço: {endereco} | Telefone: {telefone}")
        
        todas_informacoes.append([nome_empresa, endereco, telefone, link_produtos])
        

        count+=1    
        
    except:
        
        print('Nenhuma informação encontrada')
        
        pass

# Crie um DataFrame com todas as informações coletadas
df_informacoes = pd.DataFrame(todas_informacoes, columns=["Nome da Empresa", "Endereço", "Telefone", "Link"])

# Salve as informações em um arquivo Excel
df_informacoes.to_excel("informacoes_produtos.xlsx", index=False)

# Feche o driver do Chrome
driver.quit()
