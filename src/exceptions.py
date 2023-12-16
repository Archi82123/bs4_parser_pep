class ParserFindTagException(Exception):
    '''Вызывается, когда парсер не может найти тег.'''
    pass


class PepStatusMismatchError(Exception):
    '''Вызывается если ожидаемый статус и в карточке pep не совпадают'''
    def __init__(self, pep_status, expected_statuses):
        self.pep_status = pep_status
        self.expected_statuses = expected_statuses
        super().__init__((f'Несовпадающие статусы: '
                         f'Статус в карточке - {pep_status}, '
                          f'Ожидаемый статус - {expected_statuses}'))
