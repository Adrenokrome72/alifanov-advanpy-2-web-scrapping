import requests
from bs4 import BeautifulSoup
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0'
}

def parse_vacancies(start_url, max_pages=None):
    vacancies = []
    page_count = 0
    while start_url and (max_pages is None or page_count < max_pages):
        response = requests.get(start_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск вакансий на странице
        vacancy_cards = soup.find_all('div', {'class': 'vacancy-card--z_UXteNo7bRGzxWVcL7y font-inter'})
        for card in vacancy_cards:
            vacancy_info = {}
            title_block = card.find('a', {'class': 'bloko-link'})
            if title_block:
                vacancy_info['link'] = title_block.get('href')
                vacancy_info['title'] = title_block.text

            salary_block = card.find('span', {'class': 'fake-magritte-primary-text--Hdw8FvkOzzOcoR4xXWni compensation-text--kTJ0_rp54B2vNeZ3CTt2 separate-line-on-xs--mtby5gO4J0ixtqzW38wh'})
            vacancy_info['salary'] = salary_block.text if salary_block else 'Не указана'

            company_block = card.find('span', {'class': 'company-info-text--vgvZouLtf8jwBmaD1xgp'})
            vacancy_info['company'] = company_block.text if company_block else 'Не указана'

            city_block = card.find('span', {'data-qa': 'vacancy-serp__vacancy-address'})
            vacancy_info['city'] = city_block.text if city_block else 'Не указан'

            # Переход на страницу вакансии и проверка наличия ключевых слов
            vacancy_response = requests.get(vacancy_info['link'], headers=headers)
            vacancy_soup = BeautifulSoup(vacancy_response.text, 'html.parser')
            vacancy_description = vacancy_soup.find('div', {'data-qa': 'vacancy-description'})
            if vacancy_description and re.search(r'Django|Flask', vacancy_description.text, re.I):
                vacancies.append(vacancy_info)

        # Переход на следующую страницу
        next_page = soup.find('a', {'data-qa': 'pager-next'})
        if next_page:
            next_page_url = next_page.get('href')
            if next_page_url:
                start_url = 'https://hh.ru' + next_page_url  # Добавляем базовый URL к относительному пути
                page_count += 1  # Увеличиваем счетчик страниц
        else:
            break  # Если следующей страницы нет, выходим из цикла

    return vacancies


# URL для начала поиска
start_url = 'https://hh.ru/search/vacancy?text=python&area=1&area=2&page=0'
max_pages = 5  # Установите максимальное количество страниц для парсинга
vacancies_list = parse_vacancies(start_url, max_pages)

# Запись результатов в JSON
with open('vacancies.json', 'w', encoding='utf-8') as f:
    json.dump(vacancies_list, f, ensure_ascii=False, indent=4)

print('Парсинг завершен. Информация сохранена в файле vacancies.json')