import math
from http import HTTPStatus
from logging import Logger

from shared.error_handling import HTTPException


class Paginator:
    def __init__(self,
                 logger: Logger,
                 page: str,
                 per_page: str
                 ) -> None:
        self.logger = logger
        self._validate_parameters(page, per_page)
        self.page = int(page)
        self.per_page = int(per_page)
        self.total = 0
        self.total_pages = 0

    def paginate(self, items_list: list) -> list:
        """
        Paginate items
        :param items_list: The list of items to paginate
        :return: paginated item list
        """
        self.logger.info("Paginating results")
        self.total = len(items_list)
        self.total_pages = math.ceil(self.total / self.per_page)

        if self.page == 1:
            return items_list[0:self.per_page]

        start_index = self.per_page * (self.page - 1)
        end_index = self.page * self.per_page
        items = items_list[start_index:end_index]
        return items

    def _validate_parameters(self, page: str, per_page: str) -> None:
        """
        Validate the page and per_page attributes
        """
        self.logger.info("Validating pagination parameters.")
        if not page.isnumeric():
            self.logger.error(f"page is not numeric {page}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                msg="page parameter must be an integer")

        if not per_page.isnumeric():
            self.logger.error(f"per_page is not numeric{per_page}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                msg="per_page parameter must be an integer")

        if int(page) <= 0:
            self.logger.error(f"pagination must start on page 1 {page}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                msg="Pagination starts on page 1")

        if int(per_page) <= 0:
            self.logger.error(f"per_page parameter must be at least 1 {per_page}")
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                                msg="per_page parameter must be at least 1")
