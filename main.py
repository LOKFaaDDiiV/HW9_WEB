import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
from model import connect, Author, Quote

PAGES = 10  # сторінок на ресурсі
BASE_URL = 'https://quotes.toscrape.com'


def scrap_and_parse(url, number_of_pages):
    final_list = []

    for page in range(1, number_of_pages + 1):
        current_page_url = f'{url}/page/{page}'
        response = requests.get(current_page_url)
        soup = BeautifulSoup(response.text, 'lxml')

        authors = soup.find_all('small', class_='author')
        quotes = soup.find_all('span', class_='text')
        tags = soup.find_all('div', class_='tags')
        links = soup.find_all('a', string='(about)')
        links_list = [link["href"] for link in links]
        birth_info = []

        for link in links_list:
            response_local = requests.get(url+link)
            soup_local = BeautifulSoup(response_local.text, 'lxml')
            date = soup_local.find_all('span', class_='author-born-date')
            location = soup_local.find_all('span', class_='author-born-location')
            description = soup_local.find_all('div', class_='author-description')
            birth_info.append((date[0].text, location[0].text, description[0].text.strip()))

        authors_text = [a.text for a in authors]
        quotes_text = [t.text for t in quotes]
        list_of_lists = []
        for tag in tags:
            tags_raw = tag.find_all('a', class_='tag')
            tags_in_list = [tr.text for tr in tags_raw]
            list_of_lists.append(tags_in_list)

        iteration_result = list(zip(authors_text, birth_info, quotes_text, list_of_lists))
        final_list += iteration_result

    return final_list


def authors_dict_list(data):
    res = []
    sort = set()

    for d in data:
        sort.add(d[:2])

    for s in sort:
        res.append({'fullname': s[0],
                    'born_date': s[1][0],
                    'born_location': s[1][1],
                    'description': s[1][2]
                    })
    return res


def quotes_dict_list(data):
    res = []

    for d in data:
        res.append({'tags': d[3],
                    'author': d[0],
                    'quote': d[2]
                    })

    return res


#  --------------------------------------------------------------------------------------------------------------------


def str_to_date(date_string: str):
    given_date_format = '%B %d, %Y'
    date_object = datetime.strptime(date_string, given_date_format).date()
    return date_object


def json_to_db():

    with open('authors.json', 'r') as fh:
        authors_doc = json.load(fh)

    with open('quotes.json', 'r') as fh:
        quotes_doc = json.load(fh)

    for author in authors_doc:
        authors = Author(fullname=author['fullname'],
                         born_date=str_to_date(author['born_date']),
                         born_location=author['born_location'],
                         description=author['description'])
        authors.save()

        for quote in quotes_doc:
            if quote['author'] == author['fullname']:
                quotes = Quote(tags=[i for i in quote['tags']],
                               quote=quote['quote'])
                quotes.author = authors
                quotes.save()

#  --------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':

    main_list = scrap_and_parse(BASE_URL, PAGES)

    e = authors_dict_list(main_list)

    h = quotes_dict_list(main_list)

    with open('quotes.json', 'w') as fh:
        json.dump(h, fh, indent=4)

    with open('authors.json', 'w') as fh:
        json.dump(e, fh, indent=4)

    json_to_db()
