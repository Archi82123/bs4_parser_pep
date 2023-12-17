from enum import Enum
from pathlib import Path

# response-константы
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'
RESPONSE_ENCODING = 'utf-8'

# Директория и формат даты и времени
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

# Форматы логирования
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'

# Для парсера
SOUP_FEATURE = 'lxml'

# Регулярное выражение для извлечения отдельно номера версии Python и статуса
VERSION_STATUS_PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

# Ожидаемые статусы для PEP
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}


# Enum для типов вывода
class OutputType(str, Enum):
    PRETTY = 'pretty'
    FILE = 'file'

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return OutputType[s]
        except KeyError:
            raise ValueError()


# HTML-теги
class HTMLTag:
    A = 'a'
    SECTION = 'section'
    DIV = 'div'
    UL = 'ul'
    LI = 'li'
    TABLE = 'table'
    TR = 'tr'
    TD = 'td'
    H1 = 'h1'
    DL = 'dl'
