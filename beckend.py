from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
import psycopg2

# Configurações do banco de dados PostgreSQL
db_settings = {
    'db_user': 'postgres', #user
    'db_password': '', #senha
    'db_host': 'localhost',  # Ou o endereço do seu servidor PostgreSQL
    'db_port': '5432',  # Porta padrão do PostgreSQL
    'db_name': 'bd_comercioSJP' #nome do banco
}

# Configurando as opções do Chrome
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Descomente esta linha se desejar executar o Chrome em modo headless

# Instalando o driver do Chrome e obtendo o caminho do executável
chrome_driver_path = ChromeDriverManager().install()

# Passando o caminho do executável do driver e as opções para o construtor
driver = webdriver.Chrome(options=options)

# Lista para armazenar os dados coletados
data_list = []

for i in range(1, 83):
    
    url = f"https://www.guiatelefone.com/search?button=&city_id=&page={i}&what=COMERCIOS&where=S%C3%A3o+Jos%C3%A9+dos+Pinhais%2C+PR"
    
    driver.get(url)
    
    # Aguarde um tempo para que a página carregue completamente, você pode ajustar esse valor conforme necessário
    sleep(3)
    
    # Obtenha o código fonte da página
    page_source = driver.page_source
    
    # Analise o código fonte com BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Encontre todos os elementos h2 e extraia os links
    h2_elements = soup.find_all('h2')
    
    for h2 in h2_elements:
        
        link = h2.find('a')['href']
        #print(link)
        
        link_produtos = f'https://www.guiatelefone.com{link}'
        print(link_produtos)

        data_list.append(link_produtos)

# Inicialize uma lista para armazenar os dados coletados
todas_informacao = []

for link_produtos in data_list:
    
    driver.get(link_produtos)
    sleep(3)
    
    try:
        nome_empresa = driver.find_element(By.CSS_SELECTOR, "body > main > section > div > div.pt-3.pb-5.mb-6.border-b.border-gray-200 > h1").text.strip()
        endereco = driver.find_element(By.CSS_SELECTOR, "body > main > section > div > div.md\:flex > div.min-w-0.grow > div.space-y-6 > div:nth-child(1) > div:nth-child(2) > p").text.strip()
        telefone = driver.find_element(By.CSS_SELECTOR, "body > main > section > div > div.md\:flex > div.min-w-0.grow > div.space-y-6 > div:nth-child(1) > div:nth-child(3) > ul > li > span > a").text.strip()
        
        print(f"Empresa: {nome_empresa} | Endereço: {endereco} | Telefone: {telefone} | Link: {link_produtos}")
        
        # Adicione os dados como uma lista
        todas_informacao.append([nome_empresa, endereco, telefone, link_produtos])
    except:
        print('Nenhuma informação encontrada para o link:', link_produtos)

# Criar um DataFrame com os dados coletados
df_informacao = pd.DataFrame(todas_informacao, columns=["Nome da Empresa", "Endereço", "Telefone", "Link"])

# Salvar os dados no banco de dados PostgreSQL
try:
    
    # Conectar ao banco de dados
    db_connection = create_engine(f'postgresql://{db_settings["db_user"]}:{db_settings["db_password"]}@{db_settings["db_host"]}:{db_settings["db_port"]}/{db_settings["db_name"]}')
    
    # Salvar o DataFrame no banco de dados (substitua "nome_da_tabela" pelo nome desejado da tabela)
    df_informacao.to_sql("table_comercios", db_connection, if_exists='replace', index=False)
    
    print("Dados salvos no banco de dados PostgreSQL com sucesso.")
except psycopg2.Error as e:
    print("Erro ao conectar ou salvar dados no banco de dados PostgreSQL:", e)
finally:
    
    # Fechar a conexão com o banco de dados
    db_connection.dispose()

# Fechar o driver do Selenium
driver.quit()
