from pilot.database.models.manga import *


def get_genres():
    genres_list = []
    for item in Manga.select():

        genres = (item.genres).split(', ')

        for genre in genres:

            if genre in genres_list:
                continue

            else:
                genres_list.append(genre)

    return sorted(genres_list, key=lambda word: word[0])


def get_manga(genre):
    result_search = Manga.select().where(Manga.genres.contains(genre))
    manga_list = []
    for item in result_search:
        only_rus = item.name.split(' (')
        manga_list.append(only_rus[0])

    return manga_list
