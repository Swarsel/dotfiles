from typing import Dict, Any
from aqt import mw


class AddonConfig:
    """The AddonConfig object loads the user configurations.

    Attributes
    ----------
    stat_colors : Dict[str, str]
        The colors for all entries in the overview table.
    date_format : str
        The format used for dates. Default: "%d.%m.%Y"
    correction_for_notes : int
        The number of note types in the deck. Counts will be divided by
        this number. Default: 1
    learn_per_day : int
        The amount of cards to be learned per day. Read from the deck's
        settings.
    show_table_for_finished_decks : bool
        Whether to show the table for finished decks. Default: True
    config: Dict[str, Any]
        Anki's config object. Used to load user configurations.
    """

    def __init__(self) -> None:
        self._initialize_default_values()
        self._refresh_date_format()
        self._refresh_stat_colors()

    def refresh(self) -> None:
        """Refreshes this object with the data in the config.

        Has to be called before assembling the table to guarantee using the
        correct settings. Fetches the user's config and updates this object's
        public attributes.
        """

        self.config = mw.addonManager.getConfig(__name__)
        if self.config is None:
            return None

        self._refresh_note_correction_factors()
        self._refresh_date_format()
        self._refresh_stat_colors()
        self._refresh_learn_per_day()
        self._refresh_show_table_for_finished_decks()

    # Initialize this object's attributes to their default values
    def _initialize_default_values(self) -> None:
        self.stat_colors: Dict[str, str] = {
            "New": "#00a",
            "Learning": "#a00",
            "Review": "#080",
            "Percent": "#888",
            "Mature": "#0051ff",
            "Young": "#0051ff",
            "Learned": "#080",
            "Unseen": "#a00",
            "Buried": "#e7a100",
            "Suspended": "#e7a100",
            "Done on Date": "#ddd",
            "Days until done": "#ddd",
            "Total": "#ddd",
        }
        self.date_format: str = "%d.%m.%Y"
        self.correction_for_notes: int = 1
        self.learn_per_day: int = 0
        self.show_table_for_finished_decks: bool = True

        self.config: Dict[str, Any] = mw.addonManager.getConfig(__name__)

    # Load the date format from the config
    def _refresh_date_format(self) -> None:
        if "Date Format" in self.config:
            if self.config["Date Format"].strip().lower() == "us":
                self.date_format = "%m/%d/%Y"
            elif self.config["Date Format"].strip().lower() == "asia":
                self.date_format = "%Y/%m/%d"
            elif self.config["Date Format"].strip().lower() == "eu":
                self.date_format = "%d.%m.%Y"
            else:
                self.date_format = self.config["Date Format"]
        else:
            self.date_format = "%d.%m.%Y"

    # Load the stat colors from the config
    def _refresh_stat_colors(self) -> None:
        if "Stat Colors" not in self.config:
            return None

        for stat, color in self.config["Stat Colors"].items():
            if stat in self.stat_colors:
                self.stat_colors[stat] = color

    # Load the note correction factors from the config
    def _refresh_note_correction_factors(self) -> None:
        if "Note Correction Factors" not in self.config:
            return None

        current_deck_name: str = mw.col.decks.current()["name"]
        last_match_length: int = 0

        for fragment, factor in self.config["Note Correction Factors"].items():
            if current_deck_name.startswith(fragment):
                if len(fragment) > last_match_length:
                    self.correction_for_notes = int(factor)
                    last_match_length = len(fragment)

        # Prevent division by zero and negative results
        if self.correction_for_notes <= 0:
            self.correction_for_notes = 1

    # Load the learn per day count from the deck's settings
    def _refresh_learn_per_day(self) -> None:
        # Try new method first (Added in Anki 2.1.45)
        try:
            current_deck_id = mw.col.decks.current()["id"]
            self.learn_per_day = mw.col.decks.config_dict_for_deck_id(current_deck_id)[
                "new"
            ]["perDay"]
            return None
        except Exception:
            # Use old deprecated method if the newer one doesn't exist
            try:
                self.learn_per_day = mw.col.decks.confForDid(current_deck_id)["new"][
                    "perDay"
                ]
            except Exception as e:
                print(e)

    # Load the "Show table for finished decks" flag from the config
    def _refresh_show_table_for_finished_decks(self) -> None:
        flag_entry: str = "Show table for finished decks"

        config_has_flag: bool = flag_entry in self.config
        flag_is_true: bool = self.config.get(flag_entry, True)

        self.show_table_for_finished_decks = config_has_flag and flag_is_true
