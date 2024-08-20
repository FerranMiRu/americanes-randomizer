import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, simpledialog

import sv_ttk
from sqlalchemy.orm import Session

from americanes_randomizer.db import controller
from americanes_randomizer.db.models import BaseModel, Player
from americanes_randomizer.db.session import DATABASE_SESSION, ENGINE
from americanes_randomizer.schemas import CreatePlayer, UpdatePlayer


def create_tables():
    """Create tables in the database"""
    BaseModel.metadata.create_all(bind=ENGINE)


class PlayerListbox(ttk.Frame):
    def __init__(self, parent: ttk.Frame, players: list[Player], db: Session, **kwargs):
        self.root = parent
        super().__init__(parent, **kwargs)
        self.db = db
        self["style"] = "Card.TFrame"
        self.selected_players = []

        self.generate_listbox(players)

    def generate_listbox(self, players: list[Player]):
        for widget in self.winfo_children():
            widget.destroy()

        players.sort(key=lambda x: x.name)
        self.listed_players = players

        for player in players:
            player_name_label = ttk.Label(self, text=f"{player.name:<50}")
            player_level_label = ttk.Label(self, text=f"{player.level:<3}")
            # update_button = ttk.Button(
            #     self, text="✏️", command=lambda: self.delete_player(player)
            # )
            # select_button = ttk.Button(
            #     self, text="➕", command=lambda: self.select_player(player)
            # )
            # delete_button = ttk.Button(
            #     self, text="❌", command=lambda: self.delete_player(player)
            # )
            update_button = ttk.Button(
                self, text="U", command=lambda p=player: self.update_player(p)
            )
            select_button = ttk.Button(
                self, text="S", command=lambda p=player: self.select_player(p)
            )
            delete_button = ttk.Button(
                self, text="D", command=lambda p=player: self.delete_player(p)
            )

            player_name_label.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)
            player_level_label.place(in_=player_name_label, relx=1.04, rely=0)
            update_button.place(in_=player_level_label, relx=1.2, rely=-0.5)
            select_button.place(in_=update_button, relx=1.2, rely=0)
            delete_button.place(in_=select_button, relx=1.2, rely=0)

    def update_player(self, player: Player):
        new_player_level = simpledialog.askstring("Update player", "New level:", parent=self)

        if new_player_level:
            controller.update_player(player.name, UpdatePlayer(level=new_player_level), self.db)

            self.generate_listbox(self.listed_players)

    def delete_player(self, player: Player):
        self.listed_players.remove(player)
        controller.delete_player(player.name, self.db)

        self.generate_listbox(self.listed_players)

    def select_player(self, player: Player):
        self.selected_players.append(player)


class AmericanesRandomizerApp(ttk.Frame):
    def __init__(self, parent, db: Session):
        super().__init__(parent, padding=10)
        parent.geometry("1100x650")

        self.db = db

        self.add_player_addition_and_americana().pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.add_database_list().pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def add_database_list(self):
        database_list_frame = ttk.Frame(self, style="Card.TFrame", padding=15)

        database_search_button = ttk.Button(
            database_list_frame, text="Search", command=self.list_players
        )
        self.database_name_search = ttk.Entry(database_list_frame, width=50, justify=tk.LEFT)
        self.database_level_search = ttk.Combobox(
            database_list_frame, values=self.get_unique_db_levels(), width=4, justify=tk.CENTER
        )
        self.database_level_search.current(0)
        self.player_listbox = PlayerListbox(database_list_frame, [], self.db)

        database_list_frame.columnconfigure(0, weight=1, pad=2)
        database_list_frame.columnconfigure(1, weight=1, pad=2)
        database_list_frame.rowconfigure(0, weight=1, pad=5)
        database_list_frame.rowconfigure(1, weight=100, pad=5)

        self.database_name_search.grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        self.database_level_search.grid(row=0, column=1, sticky=tk.W)
        database_search_button.place(
            in_=self.database_level_search, relx=1.9, rely=0.5, anchor=tk.E
        )
        self.player_listbox.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)

        self.list_players()

        return database_list_frame

    def add_player_addition_and_americana(self):
        player_addition_and_americana_frame = ttk.Frame(self, style="Card.TFrame", padding=15)

        self.player_label = ttk.Label(player_addition_and_americana_frame, text="Player:")
        self.level_label = ttk.Label(player_addition_and_americana_frame, text="Level:")
        self.player_entry = ttk.Entry(player_addition_and_americana_frame, width=50)
        self.level_entry = ttk.Entry(player_addition_and_americana_frame, width=4)
        self.add_button = ttk.Button(
            player_addition_and_americana_frame, text="Add Player", command=self.add_player
        )
        self.americana_label = ttk.Label(player_addition_and_americana_frame, text="Americana:")
        self.americana_entry = ttk.Entry(player_addition_and_americana_frame)
        self.randomize_button = ttk.Button(
            player_addition_and_americana_frame, text="Randomize", command=self.randomize
        )

        player_addition_and_americana_frame.columnconfigure(0, weight=1, pad=2)
        player_addition_and_americana_frame.rowconfigure(0, weight=1, pad=5)
        player_addition_and_americana_frame.rowconfigure(1, weight=1, pad=5)

        self.player_entry.grid(row=0, column=0, padx=2, pady=10, sticky=tk.NW)
        self.player_label.place(in_=self.player_entry, relx=0, rely=-0.5, anchor=tk.W)

        self.level_entry.grid(row=0, column=0, padx=2, pady=10, sticky=tk.NE)
        self.level_label.place(in_=self.level_entry, relx=0, rely=-0.5, anchor=tk.W)
        self.add_button.place(in_=self.level_entry, relx=1, rely=2, anchor=tk.E)

        # self.americana_label.pack()
        # self.americana_entry.pack()
        # self.randomize_button.pack()

        return player_addition_and_americana_frame

    def randomize(self):
        pass

    def get_unique_db_levels(self):
        levels = controller.list_levels(self.db)
        levels.sort()
        return ["All"] + levels if levels else ["All"]

    def add_player(self):
        player = self.player_entry.get()
        level = self.level_entry.get()

        if player and level:
            controller.create_new_player(CreatePlayer(name=player, level=level), self.db)

            self.list_players()
            self.database_level_search["values"] = self.get_unique_db_levels()

            self.player_entry.delete(0, tk.END)
            self.level_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Please input a player and level.")

    def list_players(self):
        search_name = self.database_name_search.get()
        search_level = self.database_level_search.get()

        if search_level == "All":
            search_level = None

        retrieved_players = controller.list_players(search_name, search_level, self.db)

        self.player_listbox.generate_listbox(retrieved_players)


def main():
    create_tables()

    root = tk.Tk()
    root.title("Americanes Randomizer 3000")

    sv_ttk.set_theme("dark")

    with DATABASE_SESSION() as db:
        AmericanesRandomizerApp(root, db).pack(expand=True, fill="both")
        root.mainloop()


if __name__ == "__main__":
    main()
