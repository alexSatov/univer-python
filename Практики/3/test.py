from urllib.request import urlopen
from urllib.parse import quote
from urllib.parse import unquote
from urllib.error import URLError, HTTPError
import re


def get_content(name):
    link = 'https://ru.wikipedia.org/wiki/{}'.format(quote(name))
    try:
        content = urlopen(link).read().decode('utf-8')
    except (URLError, HTTPError):
        return None
    return content


def extract_content(page):
    artical_begin = re.search(r'<div id="content".*?', page)
    artical_end = re.search(r'<h2><span.*?>Ссылки</span>', page)
    if artical_begin is None:
        return 0, 0
    else:
        return artical_begin.end(), artical_end.start()


def extract_links(page, begin, end):
    all_links = set(re.findall(r'["\']/wiki/([\w%]+?)["\']', page[begin:end]))
    correct_links = set()
    for link in all_links:
        correct_links.add(unquote(link))
    return correct_links


def find_chain(start, finish):
    """
    Функция принимает на вход название начальной и конечной статьи и возвращает
    список переходов, позволяющий добраться из начальной статьи в конечную.
    Первым элементом результата должен быть start, последним — finish.
    Если построить переходы невозможно, возвращается None.
    """
    start = start[0].upper() + start[1:]
    finish = finish[0].upper() + finish[1:]
    current_state = start
    path = []
    if start == finish:
        path.append(start)
        return path
    return searching(current_state, path, finish)


def searching(current_state, path, finish):
        path.append(current_state)
        page = get_content(current_state)
        article_borders = extract_content(page)
        links = extract_links(page, *article_borders)
        for link in links:
            if link == finish:
                path.append(link)
                return path
        for link in links:
            if link not in path:
                searching(link, path, finish)


page = get_content('Философия')
borders = extract_content(page)
links = extract_links(page, *borders)
for x in links:
    print(x)

