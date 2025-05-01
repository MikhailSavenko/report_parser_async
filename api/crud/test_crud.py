from base_crud import CRUDBase
from db.models import SpimexTradingResult


class CrudTestRepository(CRUDBase):
    pass


crud_test_repository = CrudTestRepository(SpimexTradingResult)