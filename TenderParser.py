import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import pandas as pd

SITE_URL = 'https://zakupki.gov.ru'
RESULT_FILENAME = 'Tenders.xlsx'


def get_tenders_list(date, phrases_list):
    tenders_list_html = []
    for phrase in phrases_list:
        keywords = '+'.join(phrase.split(' '))
        tenders_list_url = SITE_URL + f'/epz/order/extendedsearch/results.html?searchString={keywords}&morphology=on&pageNumber=1&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&fz223=on&fz94=on&af=on&currencyIdGeneral=-1&publishDateFrom={date}'
        try:
            response = requests.get(tenders_list_url, headers={'User-Agent': UserAgent().chrome})
        except:
            return []
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        tenders_list_html.extend(soup.findAll('div', class_='search-registry-entry-block box-shadow-search-input'))
    return tenders_list_html


def get_tender_attributes(tender, attr_name):
    if attr_name == 'region':
        try:
            link = SITE_URL + tender.find('div', class_='registry-entry__header-mid__number').a['href']
            response = requests.get(link, headers={'User-Agent': UserAgent().chrome})
            if not response.ok:
                return []
            html = response.content
            soup = BeautifulSoup(html, 'html.parser')
            region = soup.find('span', text=lambda x: x and 'Регион' in x).next_sibling.next_sibling.text.strip()
            return region
        except:
            return '[не найдено]'
    elif attr_name == 'description':
        try:
            description = tender.find('div', class_='registry-entry__body-value').text.strip()
            return description
        except:
            return '[не найдено]'
    elif attr_name == 'customer':
        try:
            customer = tender.find('div', class_='registry-entry__body-href').text.strip()
            return customer
        except:
            return '[не найдено]'
    elif attr_name == 'start_from':
        try:
            start_from = tender.find('div', text=lambda x: x and 'Размещено' in x).next_sibling.next_sibling.text.strip()
            return start_from
        except:
            return '[не найдено]'
    elif attr_name == 'active_to':
        try:
            active_to = tender.find('div', text=lambda x: x and 'Окончание подачи заявок' in x).next_sibling.next_sibling.text.strip()
            return active_to
        except:
            return '[не найдено]'
    elif attr_name == 'tender_type':
        try:
            tender_type = tender.find('div', class_='col-9 p-0 registry-entry__header-top__title text-truncate').text.strip().split()[0]
            return tender_type
        except:
            return '[не найдено]'
    elif attr_name == 'start_price':
        try:
            start_price = tender.find('div', class_='price-block__value').text.strip()
            return start_price
        except:
            return '[не найдено]'
    elif attr_name == 'link':
        try:
            link = SITE_URL + tender.find('div', class_='registry-entry__header-mid__number').a['href']
            return link
        except:
            return '[не найдено]'
    else:
        return '[не найдено]'


def set_tenders_to_df(tenders_list):
    tenders_df = pd.DataFrame(columns=['region', 'description', 'customer', 'start_from', 'active_to', 'tender_type', 'start_price', 'link'])
    for tender in tenders_list:
        adding_row = {'region': get_tender_attributes(tender, 'region'),
                      'description': get_tender_attributes(tender, 'description'),
                      'customer': get_tender_attributes(tender, 'customer'),
                      'start_from': get_tender_attributes(tender, 'start_from'),
                      'active_to': get_tender_attributes(tender, 'active_to'),
                      'tender_type': get_tender_attributes(tender, 'tender_type'),
                      'start_price': get_tender_attributes(tender, 'start_price'),
                      'link': get_tender_attributes(tender, 'link')}
        tenders_df = tenders_df.append(adding_row, ignore_index=True)
    return tenders_df


def export_tenders_to_xls(tenders_dataframe):
    if not tenders_dataframe.empty:
        writer = pd.ExcelWriter(RESULT_FILENAME, 'xlsxwriter')
        tenders_dataframe.to_excel(writer,
                                   index=False,
                                   sheet_name='Tenders',
                                   header=['Регион',
                                           'Наименование',
                                           'Заказчик',
                                           'Дата размещения',
                                           'Подача заявок по',
                                           'Тип торгов',
                                           'Начальная цена контракта',
                                           'Ссылка на закупку'])
        workbook = writer.book
        worksheet = writer.sheets['Tenders']
        headers_row_format = workbook.add_format({'bold': True})
        wrap_column_format = workbook.add_format({'text_wrap': True,
                                                  'align': 'center',
                                                  'valign': 'vcenter'})
        worksheet.set_row(0, None, headers_row_format)
        worksheet.set_column(0, 0, 20, wrap_column_format)
        worksheet.set_column(1, 1, 60, wrap_column_format)
        worksheet.set_column(2, 2, 20, wrap_column_format)
        worksheet.set_column(3, 3, 20, wrap_column_format)
        worksheet.set_column(4, 4, 20, wrap_column_format)
        worksheet.set_column(5, 5, 10, wrap_column_format)
        worksheet.set_column(6, 6, 25, wrap_column_format)
        worksheet.set_column(7, 7, 20, wrap_column_format)


        writer.save()
        return RESULT_FILENAME
    else:
        return ''

#tl = get_tenders_list('30.03.2022', ['генеральный план', 'проект планировки'])
#tdf = set_tenders_to_df(tl)
#export_tenders_to_xls(tdf)
