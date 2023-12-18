import logging
from typing import Optional, Union

from bs4 import BeautifulSoup
from requests import RequestException, Response, Session

from constants import RESPONSE_ENCODING
from exceptions import ParserFindTagException


def get_response(session: Session, url: str) -> Optional[Response]:
    try:
        response = session.get(url)
        response.encoding = RESPONSE_ENCODING
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(
        soup: BeautifulSoup,
        tag: str,
        attrs: Optional[Union[dict, None]] = None
) -> Optional[BeautifulSoup]:
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
