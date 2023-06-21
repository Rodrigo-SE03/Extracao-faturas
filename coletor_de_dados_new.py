import PySimpleGUI as sg
import os
from PyPDF2 import PdfReader
import pandas as pd
import re
import xlsxwriter
import extrator as ext

sg.theme('Dark')   

layout = [[sg.Text('Selecione a pasta com as faturas')],
          [sg.Text('Faturas', size=(8, 1)), sg.Input(), sg.FolderBrowse()],
          [sg.Text('Selecione a pasta onde serão salvos os dados')],
          [sg.Text('Pasta', size=(8, 1)), sg.Input(), sg.FolderBrowse()],
          [sg.Text('Digite o nome da planilha com os dados')],
          [sg.Text('Nome', size=(8, 1)), sg.Input()],
          [sg.Submit(), sg.Cancel()]]

window = sg.Window('Coleta de dados', layout)


event, values = window.read()
pasta = values[0]
saida = f'{values[1]}/{values[2]}.xlsx'

'''
fatura = os.path.join(pasta,'04-22.pdf')
reader = PdfReader(fatura)           #para teste individual, inserir o nome do arquivo aqui, para gerar o total coloque    fatura
page = reader.pages[0]
texto = page.extract_text()
print(texto)
'''

def conferir(precos,preco_total):
    preco_calculado = 0 
    for preco in precos:
        preco_calculado += preco
    if (preco_calculado >= preco_total-0.05) and (preco_calculado <= preco_total+0.05):
        flag_confere = 'CONFERE'
    else:
        flag_confere = 'NÃO CONFERE'
        print("erro")
    conferir = [preco_calculado,flag_confere]
    return conferir

def definir_valor(texto):
    preco_total = float(format_number(re.search('(R\$)[\*]+([0-9,.]+)',texto).group(2)))

    data = ext.get_data(texto)
    mes,ano = data
    try:
        re.search('(GERAÇÃO)',texto).group(1)
        gen = True
    except:
        gen = False

    demanda_contratada = ext.get_demanda_contratada(texto)
    demanda_P = ext.get_demanda_hp(texto)
    demanda,preco_demanda = ext.get_demanda_hfp(texto)
    demanda_ex,preco_demanda_ex = ext.get_demanda_exd(texto,demanda,demanda_contratada)
    demanda_ultrapassagem,preco_demanda_ultrapassagem = ext.get_ultrapassagem(texto)
    consumo_hp,preco_consumo_hp = ext.get_consumo_hp(texto,gen)
    consumo_hfp,preco_consumo_hfp = ext.get_consumo_hfp(texto,gen)
    bandeiras_tipo,bandeiras = ext.get_bandeiras(texto,gen)
    consumo_reativa,preco_reativa = ext.get_energia_reativa(texto)
    dem_reativa,preco_dem_reativa = ext.get_dem_reativa(texto)
    ilum = ext.get_ilum(texto)
    valor_extra = ext.get_compesacoes(texto)
    multa = ext.get_multas(texto)
    icms,pasep,cofins = ext.get_impostos(texto)
    precos = [preco_demanda,preco_demanda_ex,preco_demanda_ultrapassagem,preco_consumo_hp,preco_consumo_hfp,bandeiras,preco_reativa,preco_dem_reativa,ilum,valor_extra,multa]
    preco_calculado,flag_confere = conferir(precos,preco_total)
    data = f'{mes}/{ano}'
    maior_que = demanda_P if demanda_P>demanda else demanda

    valores = [data,demanda_P,demanda,preco_demanda,maior_que,demanda_ex,preco_demanda_ex,demanda_ultrapassagem,preco_demanda_ultrapassagem,consumo_hp,preco_consumo_hp,consumo_hfp,preco_consumo_hfp,bandeiras_tipo,bandeiras,consumo_reativa,preco_reativa,dem_reativa,preco_dem_reativa,ilum,valor_extra,multa,icms,pasep,cofins,preco_total,preco_calculado,flag_confere]
    return valores

def format_number(num):
    num = num.replace('.','')
    num = num.replace(',','.')
    return float(num)

def definir_colunas(classificacao):
    if classificacao == 'Verde':
        planilha = {'Data': [],
            'Demanda Registrada HP':[],
            'Demanda Ativa HFP/Único HFP kW':[],
            'Demanda Ativa HFP/Único R$': [],
            'Maior Entre kW':[],
            'Demanda Ativa HFP/Único S/ICMS kW':[],   # CALCULADO NA PLANILHA -- NÃO PREENCHER
            'Demanda Ativa HFP/Único S/ICMS R$':[],
            'Ultrapassagem Demanda kW':[], 
            'Ultrapassagem Demanda R$':[],
            'Consumo Energia Ativa HP kWh':[],
            'Consumo Energia Ativa HP  R$':[],
            'Consumo Energia Ativa HFP kWh':[],
            'Consumo Energia Ativa HFP  R$':[],
            'Bandeira Tarifária TIPO':[],             # CALCULADO NA PLANILHA -- NÃO PREENCHER
            'Bandeira Tarifária R$':[],
            'Energia Reativa kWh':[],
            'Energia Reativa R$':[],
            'Demanda Reativa kWh':[],
            'Demanda Reativa R$':[],
            'Contribuição iluminação pública':[],
            'Compensações Diversas':[],
            'Multa por atraso':[],
            'ICMS':[],
            'PASEP':[],
            'COFINS':[],
            'VALOR TOTAL':[],
            'VALOR CALCULADO':[],
            'CONFERÊNCIA DE VALORES':[],
            }
    return planilha


def inserir_valores(colunas,valores):
    num=0
    for coluna,item in colunas.items():
        item.append(valores[num])
        num+=1

def cor_bandeira(val):
    bg_color = '#FFC7CE' if val == "VERMELHA" else '#C6EFCE'
    color = '#9C0006' if val == "VERMELHA" else '#006100'
    return f'background-color: {bg_color}; color: {color}'

def cor_geral(val):
    bg_color = '#92D050' if val != "NÃO CONFERE" else '#FFC7CE'
    return f'background-color: {bg_color}'

planilha = definir_colunas('Verde')

for arquivo in os.listdir(pasta):
    fatura = os.path.join(pasta,arquivo)
    reader = PdfReader(fatura)           #para teste individual, inserir o nome do arquivo aqui, para gerar o total coloque    fatura
    page = reader.pages[0]
    texto = page.extract_text()
    #print(texto)

    valores = definir_valor(texto)
    inserir_valores(planilha,valores)

df = pd.DataFrame(data = planilha)
pd.set_option('display.max_colwidth', None)
writer = pd.ExcelWriter(saida, engine="xlsxwriter")


s = df.style.applymap(cor_geral).applymap(cor_bandeira,subset=pd.IndexSlice[:,['Bandeira Tarifária TIPO']]).set_properties(**{'text-align': 'center'}).set_properties(subset=['Data','VALOR TOTAL','VALOR CALCULADO'], **{'background-color': 'white'})

df.to_excel(writer, sheet_name='Sheet1')
workbook = writer.book
worksheet = writer.sheets['Sheet1']

border_fmt = workbook.add_format({'bottom':1, 'top':1, 'left':1, 'right':1})
worksheet.conditional_format(xlsxwriter.utility.xl_range(0, 0, len(df), len(df.columns)), {'type': 'no_errors', 'format': border_fmt})

s.to_excel(writer, sheet_name='Sheet1')

writer.close()



#Após determinar a classificação tarifária e se há geração própria, será montado o dicionário contendo as colunas respectivas (é preciso adicionar a coluna de "mês");
#Será criada uma função principal para atribuir os valores de cada coluna, nela vão estar presentes as condições (ex: se for azul adiciona a demanda na ponta e fora da ponta);
#No cálculo da demanda excedente é preciso considerar a maior demanda (entre hp e hfp)