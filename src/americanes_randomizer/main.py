import math
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from tkinter import messagebox, simpledialog

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from americanes_randomizer.constants import (
    ButtonEmojis,
    Levels,
    ListPurposes,
    PaginationOptions,
    SearchLevelOptions,
)
from americanes_randomizer.db import controller
from americanes_randomizer.db.models import BaseModel, Player
from americanes_randomizer.db.session import DATABASE_SESSION, ENGINE
from americanes_randomizer.randomize_logic import distribute_americana
from americanes_randomizer.schemas import CreatePlayer, UpdatePlayer


def create_tables():
    """Create tables in the database"""
    BaseModel.metadata.create_all(bind=ENGINE)


class PlayerListbox(ttk.Frame):
    def __init__(
        self,
        parent: ttk.Frame,
        players: list[Player],
        list_purpose: ListPurposes,
        page_limit: int,
        db: Session,
        **kwargs,
    ):
        self.root = parent
        super().__init__(parent, **kwargs)

        self.db = db
        self.list_purpose = list_purpose
        self.page_limit = page_limit

        self.page_index = 0
        self["style"] = "Card.TFrame"
        self.selected_players = []

        self.update_players(players)

    def show_players_page(self, direction: PaginationOptions):
        if direction == PaginationOptions.FIRST:
            self.page_index = 0
        elif direction == PaginationOptions.NEXT:
            self.page_index += 1
            if self.page_index not in self.paginated_players:
                self.page_index -= 1
        elif direction == PaginationOptions.PREVIOUS:
            self.page_index -= 1
            if self.page_index not in self.paginated_players:
                self.page_index += 1
        elif direction == PaginationOptions.LAST:
            self.page_index = max(self.paginated_players.keys())
        elif direction == PaginationOptions.SAME:
            if self.page_index not in self.paginated_players:
                self.page_index = max(self.paginated_players.keys())

        if self.paginated_players:
            self._generate_listbox()

    def update_players(
        self, players: list[Player], direction: PaginationOptions = PaginationOptions.SAME
    ):
        if players:
            self.players = players
            if self.list_purpose == ListPurposes.DATABASE:
                self.players.sort(key=lambda x: x.name.lower())

            self.paginated_players = {
                math.floor(int(i / self.page_limit)): self.players[i : i + self.page_limit]
                for i in range(0, len(self.players), self.page_limit)
            }

            self.show_players_page(direction)
        else:
            for widget in self.winfo_children():
                widget.destroy()

    def _generate_listbox(self):
        for widget in self.winfo_children():
            widget.destroy()

        for player in self.paginated_players[self.page_index]:
            player_name_label = ttk.Label(self, text=f"{player.name:<50}", width=52)
            player_level_label = ttk.Label(self, text=f"{player.level.value:<3}", width=4)

            player_name_label.pack(side=tk.TOP, anchor=tk.W, padx=(5, 3), pady=9)
            player_level_label.place(in_=player_name_label, relx=1, rely=0)

            if self.list_purpose == ListPurposes.DATABASE:
                select_button = ttk.Button(
                    self,
                    text=ButtonEmojis.ADD.value,
                    command=lambda p=player: self.root.master.select_player(p),
                    width=3,
                )
                update_button = ttk.Button(
                    self,
                    text=ButtonEmojis.EDIT.value,
                    command=lambda p=player: self._update_player(p),
                    width=3,
                )
                delete_button = ttk.Button(
                    self,
                    text=ButtonEmojis.DELETE.value,
                    command=lambda p=player: self._delete_player(p),
                    width=3,
                )

                select_button.place(in_=player_level_label, relx=1.1, rely=-0.3)
                update_button.place(in_=select_button, relx=1.1, rely=0)
                delete_button.place(in_=update_button, relx=1.1, rely=0)

            elif self.list_purpose == ListPurposes.SELECTED:
                deselect_button = ttk.Button(
                    self,
                    text=ButtonEmojis.CANCEL.value,
                    command=lambda p=player: self.root.master.deselect_player(p),
                    width=3,
                )

                deselect_button.place(in_=player_level_label, relx=1.1, rely=-0.3)

        self.previous_button = ttk.Button(
            self,
            style="Accent.TButton",
            text=ButtonEmojis.PREVIOUS.value,
            command=lambda: self.show_players_page(PaginationOptions.PREVIOUS),
            width=12,
        )
        self.page_counter = ttk.Label(
            self, text=f"{self.page_index + 1} / {len(self.paginated_players)}"
        )
        self.next_button = ttk.Button(
            self,
            style="Accent.TButton",
            text=ButtonEmojis.NEXT.value,
            command=lambda: self.show_players_page(PaginationOptions.NEXT),
            width=12,
        )

        self.previous_button.pack(side=tk.LEFT, anchor=tk.SW, pady=(5, 0))
        if self.list_purpose == ListPurposes.DATABASE:
            self.page_counter.pack(side=tk.LEFT, anchor=tk.S, pady=10, padx=(160, 0))
        elif self.list_purpose == ListPurposes.SELECTED:
            self.page_counter.pack(side=tk.LEFT, anchor=tk.S, pady=10, padx=(130, 0))
        self.next_button.pack(side=tk.RIGHT, anchor=tk.SE, pady=(5, 0))

    def _delete_player(self, player: Player):
        delete_confirmation = messagebox.askyesno(
            title="Delete player", message=f"Are you sure you want to delete {player.name}?"
        )

        if delete_confirmation:
            controller.delete_player(player.name, self.db)
            self.players.remove(player)

            self.update_players(self.players)

    def _update_player(self, player: Player):
        new_player_level = simpledialog.askstring("Update player", "New level:", parent=self)

        if new_player_level:
            try:
                updated_player = controller.update_player(
                    player.name, UpdatePlayer(level=new_player_level), self.db
                )

                for p in self.players:
                    if p.name == player.name:
                        p.level = updated_player.level

                self.update_players(self.players)
            except (ValidationError, IntegrityError) as e:
                messagebox.showerror("Error", f"{e}")
        else:
            messagebox.showwarning("Warning", "Please input a new level.")


class AmericanesRandomizerApp(ttk.Frame):
    def __init__(self, parent, db: Session):
        super().__init__(parent, padding=10)
        parent.geometry("1110x650")
        self.db = db

        self.selected_players = []

        self.add_database_list().pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.add_player_addition_and_americana().pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    def add_database_list(self):
        database_list_frame = ttk.Frame(self, style="Card.TFrame", padding=3)

        self.database_name_search = ttk.Entry(database_list_frame, width=52, justify=tk.LEFT)
        self.database_level_search = ttk.Combobox(
            database_list_frame,
            values=[e.value for e in SearchLevelOptions],
            width=7,
            justify=tk.LEFT,
        )
        self.database_level_search.current(0)
        self.player_database = PlayerListbox(
            parent=database_list_frame,
            players=[],
            list_purpose=ListPurposes.DATABASE,
            page_limit=14,
            db=self.db,
        )
        database_search_button = ttk.Button(
            database_list_frame,
            style="Accent.TButton",
            text=ButtonEmojis.SEARCH.value,
            command=lambda: self.player_database.update_players(
                self.get_players_from_db(), PaginationOptions.FIRST
            ),
            width=3,
        )

        database_list_frame.columnconfigure(0, weight=1, pad=3)
        database_list_frame.columnconfigure(1, weight=40)
        database_list_frame.rowconfigure(0, weight=1, pad=5)
        database_list_frame.rowconfigure(1, weight=100, pad=5)
        database_list_frame.rowconfigure(2, weight=1, pad=5)

        self.database_name_search.grid(row=0, column=0, sticky=tk.W)
        self.database_level_search.grid(row=0, column=1, sticky=tk.W)
        database_search_button.place(in_=self.database_level_search, relx=2, rely=0.5, anchor=tk.E)
        self.player_database.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)

        self.player_database.update_players(self.get_players_from_db())

        return database_list_frame

    def add_player_addition_and_americana(self):
        player_addition_and_americana_frame = ttk.Frame(self, style="Card.TFrame", padding=15)

        self.player_label = ttk.Label(player_addition_and_americana_frame, text="Player:")
        self.level_label = ttk.Label(player_addition_and_americana_frame, text="Level:")
        self.player_entry = ttk.Entry(player_addition_and_americana_frame, width=52)
        self.level_entry = ttk.Combobox(
            player_addition_and_americana_frame,
            values=[e.value for e in Levels],
            width=7,
            justify=tk.LEFT,
        )
        self.add_button = ttk.Button(
            player_addition_and_americana_frame,
            style="Accent.TButton",
            text="Add Player",
            command=self.add_player,
        )
        self.selected_players_list = PlayerListbox(
            parent=player_addition_and_americana_frame,
            players=[],
            list_purpose=ListPurposes.SELECTED,
            page_limit=8,
            db=self.db,
        )
        self.americana_level_title = ttk.Label(
            player_addition_and_americana_frame, text="Americana Level:"
        )
        self.americana_level = ttk.Combobox(
            player_addition_and_americana_frame,
            values=[e.value for e in Levels],
            width=7,
            justify=tk.LEFT,
        )
        self.americana_probability_modification_title = ttk.Label(
            player_addition_and_americana_frame, text="Prob Mod:"
        )
        self.americana_probability_modification = ttk.Entry(
            player_addition_and_americana_frame, width=4, justify=tk.CENTER
        )
        self.randomize_button = ttk.Button(
            player_addition_and_americana_frame,
            style="Accent.TButton",
            text="Generate Americana",
            command=self.generate_americana,
        )

        player_addition_and_americana_frame.columnconfigure(0, weight=1, pad=2)
        player_addition_and_americana_frame.rowconfigure(0, weight=1, pad=5)
        player_addition_and_americana_frame.rowconfigure(1, weight=8, pad=5)

        self.player_entry.grid(row=0, column=0, padx=2, pady=20, sticky=tk.NW)
        self.player_label.place(in_=self.player_entry, relx=0, rely=-0.5, anchor=tk.W)

        self.level_entry.grid(row=0, column=0, padx=2, pady=20, sticky=tk.NE)
        self.level_label.place(in_=self.level_entry, relx=0, rely=-0.5, anchor=tk.W)
        self.add_button.place(in_=self.level_entry, relx=1, rely=2, anchor=tk.E)

        self.selected_players_list.grid(row=1, column=0, sticky=tk.EW)

        self.americana_level_title.grid(row=1, column=0, sticky=tk.SW, pady=5)
        self.americana_level.place(in_=self.americana_level_title, relx=1.7, rely=0.5, anchor=tk.E)
        self.americana_probability_modification_title.grid(
            row=1, column=0, sticky=tk.S, pady=5, padx=(0, 10)
        )
        self.americana_probability_modification.place(
            in_=self.americana_probability_modification_title, relx=1.7, rely=0.5, anchor=tk.E
        )
        self.americana_probability_modification.insert(0, "1")
        self.randomize_button.grid(row=1, column=0, sticky=tk.SE)

        return player_addition_and_americana_frame

    def add_player(self):
        player = self.player_entry.get()
        level = self.level_entry.get()

        if player and level:
            try:
                controller.create_new_player(CreatePlayer(name=player, level=level), self.db)
                self.player_database.update_players(self.get_players_from_db())

                self.player_entry.delete(0, tk.END)
                self.level_entry.delete(0, tk.END)
            except (ValidationError, IntegrityError) as e:
                messagebox.showerror("Error", f"{e}")
        else:
            messagebox.showwarning("Warning", "Please input a player and level.")

    def deselect_player(self, player: Player):
        self.selected_players.remove(player)

        self.selected_players_list.update_players(self.selected_players)

    def get_players_from_db(self) -> list[Player]:
        search_name = self.database_name_search.get()
        search_level = self.database_level_search.get()

        if search_level == SearchLevelOptions.ALL.value:
            search_level = None

        return controller.list_players(search_name, search_level, self.db)

    def select_player(self, player: Player):
        if player not in self.selected_players:
            self.selected_players.append(player)

            self.selected_players_list.update_players(self.selected_players)

    def generate_americana(self):
        if len(self.selected_players) < 8:
            messagebox.showwarning("Warning", "Please select at least 8 players.")
            return
        elif len(self.selected_players) % 4 != 0:
            messagebox.showwarning("Warning", "Please select a multiple of 4 players.")
            return
        elif not (americana_level_string := self.americana_level.get()):
            messagebox.showwarning("Warning", "Please select an Americana level.")
            return
        elif not (
            americana_probability_modification := self.americana_probability_modification.get()
        ):
            messagebox.showwarning("Warning", "Please input a probability modification.")
            return
        try:
            americana_probability_modification = float(americana_probability_modification)
        except ValueError:
            messagebox.showwarning("Warning", "Please input a valid probability modification.")
            return

        for level in Levels:
            if level.value == americana_level_string:
                americana_level = level

        distributed_players = distribute_americana(
            players=self.selected_players,
            probability_modification=americana_probability_modification,
            americana_level=americana_level,
        )

        americana_distribution_message = ""
        for court, players in distributed_players.items():
            americana_distribution_message += f"Court {court + 1}:\n"
            for player in players:
                americana_distribution_message += f"\t{player}\n"
            americana_distribution_message += "\n"

        is_save_americana = messagebox.askokcancel(
            title="Save Distribution?", message=americana_distribution_message
        )

        if is_save_americana:
            home_path = Path().home().resolve()
            file_name = "americana_distribution.txt"

            if (desktop_path := home_path / "Desktop").exists():
                save_path = desktop_path / file_name
            elif (desktop_path := home_path / "Escritorio").exists():
                save_path = desktop_path / file_name
            elif (desktop_path := home_path / "One Drive" / "Escritorio").exists():
                save_path = desktop_path / file_name
            elif (desktop_path := home_path / "OneDrive" / "Escritorio").exists():
                save_path = desktop_path / file_name
            else:
                save_path = Path.cwd() / file_name

            with open(save_path, "w") as f:
                f.write(americana_distribution_message)

            messagebox.showinfo(
                "Americana Distribution Saved",
                f"Americana distribution saved to {save_path}",
            )


def main():
    database_dir = Path().resolve() / "database"
    if not database_dir.exists():
        database_dir.mkdir(exist_ok=True)

    create_tables()

    root = tk.Tk()
    root.title("Americanes Randomizer 3000")

    if (Path.cwd() / "assets").exists():
        root.tk.call("source", "assets/ttk_theme/azure.tcl")
    else:
        root.tk.call("source", "_internal/assets/ttk_theme/azure.tcl")

    root.tk.call("set_theme", "light")

    with DATABASE_SESSION() as db:
        AmericanesRandomizerApp(root, db).pack(expand=True, fill=tk.BOTH)
        root.mainloop()


if __name__ == "__main__":
    main()
