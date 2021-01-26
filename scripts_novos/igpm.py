import requests
from github import Github
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import numpy as np
from datetime import datetime
import util as util
from util import *
from upload import *
 
def retorn_num_mes(mes_nome):
  if mes_nome == 'Janeiro':
    return '01'
  if mes_nome == 'Fevereiro':
    return '02'
  if mes_nome == 'Março':
    return '03'
  if mes_nome == 'Abril':
    return '04'
  if mes_nome == 'Maio':
    return '05'
  if mes_nome == 'Junho':
    return '06'
  if mes_nome == 'Julho':
    return '07'
  if mes_nome == 'Agosto':
    return '08'
  if mes_nome == 'Setembro':
    return '09'
  if mes_nome == 'Outubro':
    return '10'
  if mes_nome == 'Novembro':
    return '11'
  if mes_nome == 'Dezembro':
    return '12'

url = FONTE_IGPM
data = requests.get(url)
soup = bs(data.content, "html.parser")

qtd_tables = 1
json_igpm = []
referencia = [None] * qtd_tables
ano = [None] * qtd_tables

print('- Dados extraídos')
for table_num in range(qtd_tables):
  table = soup.find_all('table')
  df = pd.read_html(str(table), decimal=',', thousands='.')[table_num]
  ano[table_num] = df.columns[0][0]
  df.columns = df.columns.droplevel(0)
  # df1['ano']= ano
  df.drop(["Acumulado nos últimos 12 meses %"], axis=1, inplace=True)

  df.rename(columns={'MÊS': 'mes', 'Mensal %': 'mensal'}, inplace=True)
  
  data = []

  
  for index, row in df.T.iteritems():
    mes = (ano[0] + retorn_num_mes(row['mes']))
    mes = pd.to_datetime(mes, format='%Y%m', errors='coerce')
    mes = mes.strftime("%Y-%m-%dT%H:%M:%SZ")
    mensal = str(row['mensal']).replace(".", ",")
    # acumulado = str(round(row['acumulado_ano'],2)).replace(".", ",")
    
    json_igpm.append({'x': mes, 'y': float(mensal.replace(",","."))})

print('- Série criada')
##################referencia
newlist = sorted(json_igpm, key=lambda k: k['x']) 
meses_ano = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

referencia = newlist[-1:][0]['x']
ano = referencia[:4]
mes = int(referencia[5:7])
referencia = meses_ano[mes - 1] + '/' + ano

######valor cartao 
valor_cartao =newlist[-1:][0]['y']
print('- Valor do cartão armazenado')

json_igpm = {
    'nome': 'Índice Geral de Preços – Mercado (IGP-M)',
    'descricao': 'Variação percentual mensal',
    'fonte': 'FGV',
    'stats': [
        {
            'titulo': 'Brasil',
            'valor': str(valor_cartao)+'%',
            'direcao': "down" if float(valor_cartao) < 0 else "up",
            'desc_serie': 'Variação percentual mensal',
            'serie_tipo': 'data',
            'referencia': referencia,
            'y_label': {
                'prefixo_sufixo': 'sufixo',
                'label': '%'
            },
            'serie_labels': {
                'x': 'Data',
                'y': 'Variação',
            },
            'serie': newlist,
        },       
    ]
}


path_save_json = util.config['path_save_json']['path']
name_json = 'igpm'

with open(path_save_json + name_json +'.json', 'w', encoding='utf-8') as f:
    json.dump(json_igpm, f, ensure_ascii=False, indent=4)
print('- JSON armazenado')

######################################################
#Upload
upload_files_to_github(name_json)
print('- JSON enviado para o GitHub')