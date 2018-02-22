from itertools import zip_longest
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

BASE_URL = "http://speccy.piriform.com/results/"


# From itertools recipes (https://docs.python.org/3/library/itertools.html#itertools-recipes)
def _grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks"""
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def _strip_newline_elements(element_list):
    return (element for element in element_list if element != '\n')


def _wrap_singleton(items):
    if len(items) == 1:
        return items[0]

    return items[:]


def _wrap_dict_or_str(key, value):
    if not value:
        return key

    if isinstance(value, str):
        return ': '.join((key, value))

    return {key: value}


def _dict_or_list(values):
    values = list(values)
    has_values = any(v[1] for v in values)
    has_keys = any(v[0] for v in values)
    if not has_values:  # No values, only keys
        return _wrap_singleton(list(v[0] for v in values))

    if not has_keys:  # No keys, only values
        return _wrap_singleton(list(v[1] for v in values))

    if any(not v[1] for v in values):  # at least one element has an empty value
        return list(_wrap_dict_or_str(k, v) for k, v in values)

    return dict(((k or i), v) for i, (k, v) in enumerate(values))


def _parse_subsection(body):
    # At this point, 'body' should be a list of 2 divs
    # div 1: top level key-value pairs
    # div 2: subsections (pass each subsection back in to this function)
    top_level_data, subsections = _strip_newline_elements(body)
    items = []
    prev_name = 0
    for index, child in enumerate(_strip_newline_elements(top_level_data.children)):
        key, value = (c.text.strip() for c in _strip_newline_elements(child.children))

        if key.endswith(':'):
            key = key[:-1]

        if not key:
            if ': ' in value:
                key, _, value = value.partition(': ')
            else:
                items.append(value)
                continue

        if items:
            yield (prev_name, _wrap_singleton(items))
            items.clear()

        prev_name = key or index
        items.append(value)

    if items:
        yield prev_name, _wrap_singleton(items)

    for section in _grouper(_strip_newline_elements(subsections), 3):
        title, *parts = _strip_newline_elements(section)
        title = title.text.strip()
        yield title, _dict_or_list(_parse_subsection(parts))


def _parse_main_section(section):
    """
    :type section: Tag
    """
    title = section.div

    body = title.find_next('div')  # type: Tag

    return title.text.strip(), dict(_parse_subsection(body.children))


def parse(speccy_id=None, url=None, text=None, encoding=None):
    if text is None:
        if url is None:
            if speccy_id is None:
                raise ValueError("One of 'text', 'url', or 'speccy_id' must be specified")

            url = urljoin(BASE_URL, speccy_id)

        response = requests.get(url)
        response.raise_for_status()
        encoding = response.encoding
        text = response.content

        assert text

    soup = BeautifulSoup(text, 'lxml-html', from_encoding=encoding)

    body = soup.body

    content = body.div

    sections = content.find_all('div', class_="mainsection")

    data = {
        title: data for title, data in map(_parse_main_section, sections)
    }

    return data
