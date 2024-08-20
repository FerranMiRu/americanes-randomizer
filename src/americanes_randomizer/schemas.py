from pydantic import BaseModel, Field


class CreatePlayer(BaseModel):
    """Pydantic model to create players

    Attributes
    ----------
    name : str
        The name of the player, min length 3, max length 50
    level : str
        The level of the user [A, B+, B, C+, C, D], min length 1, max length 3
    """

    name: str = Field(..., min_length=3, max_length=50)
    level: str = Field(..., min_length=1, max_length=3)


class ShowPlayer(CreatePlayer):
    """Pydantic model to show players

    Attributes
    ----------
    name : str
        The name of the player, min length 3, max length 50
    level : str
        The level of the user [A, B+, B, C+, C, D], min length 1, max length 3
    """

    pass


class UpdatePlayer(BaseModel):
    """Pydantic model to update users

    Attributes
    ----------
    level : str
        The level of the user [A, B+, B, C+, C, D], min length 1, max length 3
    """

    level: str = Field(..., min_length=1, max_length=3)


class DeletePlayer(BaseModel):
    """Pydantic model to delete users

    Attributes
    ----------
    name : str
        The name of the player, min length 3, max length 50
    """

    name: str = Field(..., min_length=3, max_length=50)
