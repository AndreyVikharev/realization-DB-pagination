import requests
from bs4 import BeautifulSoup as BSoup
from pilot.database.models.manga import *
from pilot.database.db_commands import *
import os
import json


def get_data_items(url_page):

    soup = BSoup(requests.get(url_page).content, 'lxml')

    table = soup.find_all('li', attrs={'class': 'primaryContent memberListItem'})

    for item in table:
        manga_name = item.find('span', attrs={'class': 'img'})['title']

        manga_link = 'https://desu.me/' + item.find('a', attrs={'class': 'avatar NoOverlay PreviewTooltip'})['href']

        description_manga = take_manga_description(url_manga=manga_link)

        manga_cover = 'https://desu.me' + item.find('span', attrs={'class': 'img'})['style'][23:-3:1]

        list_of_genres = (item.find_all('dd')[4]).text

        rating_manga = (item.find_all('dd')[2]).text
        """Ссылка на основную страницу манги передаётся в функцию, которая вытаскивает название и ссылки на главы"""
        chapters_dict = get_chapters(url_manga=manga_link)

        """Формируем итератор и передаём в вложенный цикл для формирования класса ОРМ"""
        yield manga_name, description_manga, manga_link, manga_cover, list_of_genres, rating_manga, chapters_dict


def get_chapters(url_manga):

    soup = BSoup(requests.get(url_manga).content, 'lxml')
    chapters_list = soup.find('ul', attrs={'class': 'chlist'})
    """Формируем словарь, где ключ название а значение ссылка на главу"""
    out_dict = {}
    for chapters in chapters_list.find_all('a'):
        out_dict[chapters['title']] = 'https://desu.me/' + chapters['href']

    return out_dict


def take_manga_description(url_manga):
    soup = BSoup(requests.get(url_manga).content, 'lxml')
    description = soup.find('div', attrs={'class': 'prgrph'})

    return description.text


def collection_of_info():

    site_catalog = 'https://desu.me/manga/?order_by=popular&status=no18plus&page='
    """Основная ссылка каталога, к которой в цикле добавляется номер страницы для формирования ссылки"""
    out_data = []
    for number_page in range(4):
        url = site_catalog + str(number_page+1)
        """Ссылка передаётся в функцию, которая вытаскивает с сайта всё необходимое для формирования класса"""
        out_data.append(get_data_items(url_page=url))
    return out_data


def entry_table(input_data):
    db_manga.create_tables([Manga])
    for manga_page in input_data:
        for manga_data in manga_page:
            print('Манга', manga_data[0], 'добавлено:', len(manga_data[6]), 'главы')
            create_entry(Manga, {'name': manga_data[0],
                                 'description': manga_data[1],
                                 'link': manga_data[2],
                                 'cover': manga_data[3],
                                 'genres': manga_data[4],
                                 'rating': manga_data[5],
                                 'chapters': json.dumps(manga_data[6])
                                 }
                         )


def record_comparison(input_data):

    changelog = []
    for manga_page in input_data:
        for manga_data in manga_page:
            print(f'Проверяем: {manga_data[0]}')
            if Manga.get_or_none(Manga.name.contains(manga_data[0])):

                line_in_table = get_entry(Manga, manga_data[0])

                if float(manga_data[5]) != float(line_in_table.rating):
                    Manga.update({Manga.rating: manga_data[5]}).where(Manga.id == line_in_table.id).execute()
                    changelog.append(f'Рейтинг манги: {line_in_table.name} изменен на {manga_data[5]}')

                elif len(manga_data[6]) != len(json.loads(line_in_table.chapters)):
                    Manga.update({Manga.chapters: json.dumps(manga_data[6])}).where(Manga.id ==
                                                                                    line_in_table.id).execute()

                    changelog.append(f'Главы манги: {line_in_table.name} изменены, теперь стало - {len(manga_data[6])}')

            else:
                changelog.append(f'Манга {manga_data[0]} добавлено: {len(manga_data[6])} главы')
                create_entry(Manga, {'name': manga_data[0],
                                     'description': manga_data[1],
                                     'link': manga_data[2],
                                     'cover': manga_data[3],
                                     'genres': manga_data[4],
                                     'rating': manga_data[5],
                                     'chapters': json.dumps(manga_data[6])
                                     }
                             )
    if len(changelog):
        for change in changelog:
            print(change)
    else:
        print('Изменений нет')


def check_table(path):
    """Выполняем проверку на наличие таблицы в структуре"""
    if os.path.exists(path):

        print('Таблица находится в структуре проекта\nСобираем и проверяем дынные\n', '*' * 10, '\n')
        record_comparison(collection_of_info())
    else:
        """если БД манги нету то записываем таблицу"""
        entry_table(collection_of_info())

    db_manga.close()
