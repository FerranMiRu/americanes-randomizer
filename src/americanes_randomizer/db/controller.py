from sqlalchemy.orm import Session

from americanes_randomizer.db.models import Player
from americanes_randomizer.schemas import CreatePlayer, UpdatePlayer


def create_new_player(player: CreatePlayer, db: Session) -> Player:
    """Add a new player to the database

    Parameters
    ----------
    player : CreatePlayer
        The player to be created
    db : Session
        Database in which to put the player

    Returns
    -------
    Player
        The created player
    """
    db_player = Player(name=player.name, level=player.level)

    db.add(db_player)
    db.commit()
    db.refresh(db_player)

    return db_player


def list_players(search_name: str, search_level: str | None, db: Session) -> list[Player]:
    """Get all players that comply with the search_name and search_level from the database

    Parameters
    ----------
    db : Session
        Database in which to get the players

    Returns
    -------
    list[Player]
        A list of players
    """
    db_users = (
        db.query(Player)
        .filter(Player.name.ilike(f"%{search_name}%"))
        .filter(Player.level == search_level if search_level else True)
        .all()
    )

    return db_users


def list_levels(db: Session) -> list[str]:
    """Get all levels from the database

    Parameters
    ----------
    db : Session
        Database in which to get the levels

    Returns
    -------
    list[str]
        A list of all levels
    """
    db_levels = db.query(Player.level).distinct().all()

    return [level for (level,) in db_levels]


def update_player(name: str, player: UpdatePlayer, db: Session) -> Player | dict[str, str | int]:
    """Update a player

    Parameters
    ----------
    name : str
        The name of the player to update
    player : UpdatePlayer
        The player to update
    db : Session
        Database in which to update the player

    Returns
    -------
    Union[Player, Dict[str, Union[str, int]]]
        The updated player or a dictionary with the error
    """
    db_player = db.query(Player).filter(Player.name == name).first()

    if not db_player:
        return {"error": f"User with name {name} not found"}

    db_player.level = player.level

    db.add(db_player)
    db.commit()

    return db_player


def delete_player(name: str, db: Session) -> dict[str, str | int] | None:
    """Delete a player

    Parameters
    ----------
    name : str
        The name of the player to delete
    db : Session
        Database in which to delete the player

    Returns
    -------
    dict[str, Union[str, int]] | None
        Nothing or a dictionary with the error
    """
    db_player = db.query(Player).filter(Player.name == name).first()

    if not db_player:
        return {"error": f"Player with name {name} not found"}

    db.delete(db_player)
    db.commit()

    return None
