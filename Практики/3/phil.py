from urllib.request import urlopen
from urllib.parse import quote
from urllib.parse import unquote
from urllib.error import URLError, HTTPError
from collections import deque
import re


def get_content(name):
    link = 'https://ru.wikipedia.org/wiki/{}'.format(quote(name))
    try:
        content = urlopen(link).read().decode('utf-8')
    except (URLError, HTTPError):
        return None
    return content


def extract_content(page):
    article_begin = re.search(r'<div id="content".*?', page)
    article_end = re.search(r'<div id="mw-navigation">', page)
    if article_begin is None:
        return 0, 0
    else:
        return article_begin.end(), article_end.start()


def extract_links(page, begin, end):
    all_links = set(re.findall(r'["\']/wiki/([\w%]+?)["\']', page[begin:end]))
    correct_links = set()
    for link in all_links:
        correct_links.add(unquote(link))
    return correct_links


def find_chain(start, finish):
    queue = deque()
    queue.append(start)
    previous = {start: None}
    while len(queue) != 0:
        current_link = queue.popleft()
        page = get_content(current_link)
        if page is None:
            return None
        article_borders = extract_content(page)
        links = extract_links(page, *article_borders)
        for link in links:
            if link not in previous:
                queue.append(link)
                previous[link] = current_link
            if link == finish:
                return build_path(start, finish, previous)
    return build_path(start, finish, previous)


def build_path(start, finish, prev):
    path = [finish]
    current_link = finish
    while current_link is not start:
        current_link = prev[current_link]
        path.append(current_link)
    path.reverse()
    return path


def main():
    pass


if __name__ == '__main__':
    main()
