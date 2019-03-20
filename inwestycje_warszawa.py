
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import json

district_county = {1:'wlochy', 2:'ursus', 3:'ursynow', 4:'ochota', 5:'mokotow',6:'bemowo',
            7:'bialoleka', 8:'bielany', 9:'praga-poludnie', 10:'praga-polnoc',
            11:'rembertow', 12:'srodmiescie', 13:'targowek', 14:'wawer', 15:'wesola',
           16:'wilanow', 17:'wola', 18:'zoliborz', 19:'pruszkowski', 20:'piaseczynski',
            21:'grodziski', 22:'legionowski', 23:'minski', 24:'nowodworski', 25:'otwocki',
            26:'warszawski-zachodni', 27:'wolominski'}


def choose_districts(districts,counties):
    name_list = []
    while True:
        number = input("podaj numer dzielnicy/powiatu lub wybierz q by zakończyć: ")
        try:
            number = int(number)
            if number not in name_list:
                name_list.append(number)
        except:
            break
    for elem in name_list:
        if elem <= 18:
            districts.append(district_county[elem])
        else:
            counties.append(district_county[elem])
    return districts,counties


def create_district_list():
    districts = []
    counties = []
    choice_dc = 4
    while choice_dc not in range(1,4):
        choice_dc = int(input('Wybierz:\n1 - by wybrać dzielnice/powiaty ręcznie,\n2 - by wybrać wszystkie dzielnice i powiaty\n'))
        if choice_dc == 1:
            choose_districts(districts,counties)
        elif choice_dc == 2:
            for key in district_county:
                if key<=18:
                    districts.append(district_county[key])
                else:
                    counties.append(district_county[key])
        else:
            print('Niepoprawny wybór')
    return districts,counties


def create_url_list(districts, counties):
    url_list = []
    for county in counties:
        url = 'http://www.spisinwestycji.pl/warszawa/powiat/' + county + '/'
        url = [url,county]
        url_list.append(url)
    for district in districts:
        url = 'http://www.spisinwestycji.pl/warszawa/dzielnica/' + district + '/'
        url = [url,district]
        url_list.append(url)
    return url_list

def show_invest(inv_list): #inv_list musi być słownikiem wg wzoru z funkcji get_and_compare
    print('Lista inwestycji w wybranym miejscu:\n')
    for key, value in inv_list.items():
        print('Nazwa: %s\nAdres: %s\nStrona www: %s\n'
          % (key, value[1], value[2]))

def get_and_compare_investments(url_list):
    for url in url_list:
        response = requests.get(url[0])
        if not response.status_code == 200:
            print('url ' + url[0] + 'wygenerował błąd')
        else:
            inv_list = {}
            investments = BeautifulSoup(response.content,'lxml')
            regex = re.compile('spis-right-item dom|mieszkanie|apartament*')
            inv_tag = investments.find_all('div', class_ = regex)
            for inv in inv_tag:
                inv = re.sub('\n ','\n',inv.get_text().replace('\n\n','\n'))
                inv = re.sub('\t+| +',' ',inv)
                inv = re.sub('\n |\d{1,2}\. ','',inv)
                investment = inv.split('\n')
                inv_list[investment[1]] = [url[1],investment[2],investment[5]]
        filename = url[1]+'.json'
        try:
            with open(filename, 'r') as file:
                inv_old = json.loads(file.read())
            i = 0
            for key in inv_list:
                if key in inv_old:
                    i += 1
                    continue
                else:
                    print('%s\nPojawiła się nowa inwestycja!\n\nNazwa: %s\nAdres: %s\nStrona www: %s\n\n' % (url[1],key,inv_list[key][1],inv_list[key][2]))
            if i == len(inv_list):
                print('%s: nie ma nowych inwestycji' % url[1])
        except:
            print('\nNie śledziłeś/aś dotąd inwestycji w dzielnicy/powiecie: ' + url[1] + '\n')
            show_invest(inv_list)

        with open(filename, 'w') as file:
            file.write(json.dumps(inv_list, ensure_ascii=False))


def show_choosen_invest(districts, counties):
    for elem in districts:
        filename = elem + '.json'
        try:
            with open(filename, 'r') as file:
                inv_dict = json.loads(file.read())
            show_invest(inv_dict)
        except:
            print("\n\nNie znaleziono pliku "+ filename+".")
    for elem in counties:
        filename = elem + '.json'
        try:
            with open(filename, 'r') as file:
                inv_dict = json.loads(file.read())
            show_invest(inv_dict)
        except:
            print("\n\nNie znaleziono pliku "+ filename+".")



while True:
    districts = []
    counties = []
    print('\n')
    choice = int(input('Wybierz czynność: 1 - sprawdzenie nowych inwestycji,\n2 - wylistowanie inwestycji w wybranym miejscu z pliku json na komputerze,\n3 - zakończ program'))
    if choice == 1:
        districts,counties = create_district_list()
        url_list = create_url_list(districts, counties)
        get_and_compare_investments(url_list)
    elif choice == 2:
        for key, value in district_county.items():
            print('%i: %s' % (key, value))
        districts,counties = choose_districts(districts,counties)
        show_choosen_invest(districts,counties)
    else:
        break
