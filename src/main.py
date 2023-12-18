import logging
import re
from collections import defaultdict
from typing import List, Optional, Tuple
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from requests import Session
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL,
                       SOUP_FEATURE, VERSION_STATUS_PATTERN, HTMLTag)
from exceptions import PepStatusMismatchError
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session: Session) -> Optional[List[Tuple[str, str, str]]]:
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return None

    soup = BeautifulSoup(response.text, features=SOUP_FEATURE)

    main_div = find_tag(
        soup,
        HTMLTag.SECTION,
        attrs={'id': 'what-s-new-in-python'}
    )
    div_with_ul = find_tag(
        main_div,
        HTMLTag.DIV,
        attrs={'class': 'toctree-wrapper'}
    )
    sections_by_python = div_with_ul.find_all(
        HTMLTag.LI,
        attrs={'class': 'toctree-l1'}
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, HTMLTag.A)
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)

        response = get_response(session, version_link)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, features=SOUP_FEATURE)
        h1 = find_tag(soup, HTMLTag.H1)
        dl = find_tag(soup, HTMLTag.DL)
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )

    return results


def latest_versions(session: Session) -> Optional[List[Tuple[str, str, str]]]:
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return None

    soup = BeautifulSoup(response.text, features=SOUP_FEATURE)
    sidebar = find_tag(
        soup,
        HTMLTag.DIV,
        attrs={'class': 'sphinxsidebarwrapper'}
    )
    ul_tags = sidebar.find_all(HTMLTag.UL)
    for ul in ul_tags:
        if 'All versions' not in ul.text:
            raise Exception('Ничего не нашлось')
        a_tags = ul.find_all(HTMLTag.A)

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(VERSION_STATUS_PATTERN, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''

        results.append(
            (link, version, status)
        )

    return results


def download(session: Session) -> None:
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features=SOUP_FEATURE)

    main_tag = find_tag(soup, HTMLTag.DIV, attrs={'role': 'main'})
    table_tag = find_tag(main_tag, HTMLTag.TABLE, attrs={'class': 'docutils'})

    pdf_a4_tag = find_tag(
        table_tag,
        HTMLTag.A,
        attrs={'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session: Session) -> Optional[List[Tuple[str, int]]]:
    response = get_response(session, PEP_URL)
    if response is None:
        return None

    soup = BeautifulSoup(response.text, features=SOUP_FEATURE)

    main_section = find_tag(soup, HTMLTag.SECTION, attrs={'id': 'pep-content'})
    main_table = find_tag(
        main_section,
        HTMLTag.SECTION,
        attrs={'id': 'numerical-index'}
    )
    pep_table = find_tag(main_table, HTMLTag.TBODY)
    rows = pep_table.find_all(HTMLTag.TR)

    results = [('Статус', 'Количество')]
    status_count = defaultdict(int)
    for row in tqdm(rows):
        status = find_tag(row, HTMLTag.TD).text[1:]

        pep_suffix = find_tag(
            row,
            HTMLTag.A,
            attrs={'class': 'pep reference internal'}
        )['href']
        pep_link = urljoin(PEP_URL, pep_suffix)
        response = get_response(session, pep_link)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, features=SOUP_FEATURE)
        main_pep_section = find_tag(
            soup,
            HTMLTag.SECTION,
            attrs={'id': 'pep-content'}
        )
        pep_info_table = find_tag(main_pep_section, HTMLTag.DL)
        pep_status = pep_info_table.find(
            string='Status'
        ).find_parent().find_next_sibling().text
        try:
            if pep_status not in EXPECTED_STATUS[status]:
                raise PepStatusMismatchError(
                    pep_status,
                    EXPECTED_STATUS[status]
                )
            status_count[pep_status] += 1
        except PepStatusMismatchError as e:
            logging.error(str(e))

    status_total = list(status_count.items())
    for status in status_total:
        results.append(status)

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main() -> None:
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()

    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
