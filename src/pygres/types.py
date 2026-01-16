from typing import TypeVar
from pygres.models.base_model import PydanticTypeModel

ModelT = TypeVar("ModelT", bound=PydanticTypeModel)
