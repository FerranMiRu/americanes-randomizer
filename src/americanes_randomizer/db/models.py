from typing import Any

from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative


@as_declarative()
class BaseModel:
    """Model to serve as a base for all other database models"""

    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """To generate tablename from classname"""
        return cls.__name__.lower()


class Player(BaseModel):
    """Database model for players

    Attributes
    ----------
    name : str
        The name of the player, primary key
    level : str
        The level of the player [A, B+, B, C+, C, D]
    """

    name = Column(String, primary_key=True)
    level = Column(String, nullable=False)
