import pandas as pd
import pyodbc
import datetime
import os
from jinja2 import Template
from WBTS_initialization import WBTS
from WCELL_initialization import WCELL
from secret import *


bs_name_input = input('Введите название БС: ')
bs_type = input('Введите тип БС (normal, flexi, micro): ')
name_folder = f'{bs_name_input}___{datetime.date.today()}'


connect_rp_db = pyodbc.connect(rpdb_sql)
connect_ts_db = pyodbc.connect(ts_sql)

query_rpdb = Template(open('template/SQL_rpdb.txt', encoding='utf-8').read()).render(bs_name_input=bs_name_input)
query_tsdb = Template(open('template/SQL_ts.txt').read()).render(bs_name_input=bs_name_input.replace('_', ' '))

rpdb_bd = pd.read_sql(query_rpdb, connect_rp_db)
bcf_file = pd.read_sql(query_tsdb, connect_ts_db)

# Считаю сколько 3G БС (системников) в BCF
amount_bs_bcf = [row['3G_ID'] for index, row in bcf_file.iterrows()]

# Создаю все 3G соты из rpdb как обьект класса
for index, row in rpdb_bd.iterrows():
    WCELL(row)

# заполнить азимуты та где их нет (на 2, 3 несущих)
WCELL.azimuth_23_carrier(WCELL.WCELL_rpdb_lst)


os.mkdir(f'C:\Python\Create_3G_NSN\{name_folder}')

# Если WBTS в BCF не найдено
if len(amount_bs_bcf) == 0:
    print('No WBTS found in BCF file. Please check BCF')

# Если в BCF один WBTS
elif len(amount_bs_bcf) == 1:
    for index, row in bcf_file.iterrows():
        if row['NamePoint'] == bs_name_input.replace('_', ' '):
            WBTS_Object = WBTS(bs_name_input, row, name_folder)  # Создаю обьект WBTS и в нём файл IPNB
            # Вызываю метод для создания файла WCELL (создаются все CI из RPDB)
            WCELL.create_wcell(WBTS_Object, WCELL.WCELL_rpdb_lst, name_folder, bs_type)

# Если в BCF больше одного WBTS
elif len(amount_bs_bcf) > 1:
    for index, row in bcf_file.iterrows():
        if row['NamePoint'] == bs_name_input.replace('_', ' ') and row['3G_ID'] != 'nan':
            print('================================================================')
            if input(f"В bcf найден WBTS с номером: {int(row['3G_ID'])}. Создаём ?\n(Ответить: yes/no): ") == 'yes':
                WBTS_Object = WBTS(bs_name_input, row, name_folder)     # создаю обьект WBTS и в нём файл IPNB

                # Показываю для User все CI из рпдб
                lst_rpdb_ci = [i.CI for i in WCELL.WCELL_rpdb_lst]
                print(f'Список CI в рпдб: {lst_rpdb_ci}')

                # Спрашиваю у User какие CI создать в связке с данным WBTS и IPNB и перевожу их в список
                lst_inp_ci = input('Введите CI которые нужно создать в данном WBTS. \nCI (через запятую): ')
                lst_inp_ci = [int(i) for i in lst_inp_ci.replace(' ', '').split(',')]

                # прохожусь по изначальному списку CI, если CI есть в списке юзера доб. в список для Созд. WCELL file
                correct_wcell_pack = [i for i in WCELL.WCELL_rpdb_lst if i.CI in lst_inp_ci]
                # Вызываю метод для создания файла WCELL (CI берутся из списка correct_wcell_pack)
                name_u = input('Введите номер WBTS_Name (U1,U2,U3...): ')
                WCELL.create_wcell(WBTS_Object, correct_wcell_pack, name_folder, bs_type, name_u)





