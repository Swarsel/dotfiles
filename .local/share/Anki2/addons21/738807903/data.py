from typing import List, Dict
from .config import AddonConfig
from datetime import date, timedelta
import math
import time
from aqt.utils import showInfo
from aqt import mw


class DeckData:
    """The DeckData object assembles the active deck's data.

    Parameters
    ----------
    config : AddonConfig
        Object used to load the addon's user configuration.

    Attributes
    ----------
    labels : Dict[str, str]
        The labels for all entries in the overview table.
    stats : Dict[str, int]
        The counts of the respective card states returned by Anki's db.
    dates : Dict[str, str]
        The approximate number of days left and the date the deck will be finished on.
    percentages : Dict[str, float]
        The relative counts of the respective card states returned by Anki's db.
    percentages_without_suspended : Dict[str, float]
        The percentages when excluding suspended cards from all counts.
    """

    def __init__(self, config: AddonConfig) -> None:
        self._config = config

        self.labels: Dict[str, str] = self._get_labels()
        self.stats: Dict[str, int] = {}
        self.dates: Dict[str, str] = {}
        self.percentages: Dict[str, float] = {}
        self.percentages_without_suspended: Dict[str, float] = {}

    def refresh(self) -> None:
        """Refreshes this object with the current deck's data.

        Has to be called before assembling the table to guarantee using the
        correct data. Fetches the active deck's data and updates this
        object's public attributes.
        """

        self._config.refresh()
        self._refresh_stats()
        self._refresh_percentages()
        self._refresh_percentages_without_suspended()

    def is_finished(self) -> bool:
        """Whether the currently active deck is done for today.

        Has to be called before assembling the table to guarantee using the
        correct data. Fetches the active deck's data and updates this
        object's public attributes.

        Returns
        -------
        bool
            True if deck is done, False otherwise.
        """

        return not sum(self._get_scheduled_counts())

    def is_empty_deck(self) -> bool:
        """Whether the currently active deck is empty.

        Returns
        -------
        bool
            True if deck is empty, False otherwise.
        """

        return not self.stats["total"]

    # Return the table entry labels
    def _get_labels(self) -> Dict[str, str]:
        labels: Dict[str, str] = {}

        labels["mature"] = "Mature"
        labels["young"] = "Young"
        labels["unseen"] = "Unseen"
        labels["buried"] = "Buried"
        labels["suspended"] = "Suspended"

        labels["total"] = "Total"
        labels["learned"] = "Learned"
        labels["unlearned"] = "Unlearned"

        labels["new"] = "New"
        labels["learning"] = "Learning"
        labels["review"] = "Review"
        labels["due"] = "Due"

        labels["doneDate"] = "Done in"

        for key in labels:
            labels[key] = "{:s}:".format(labels[key])

        return labels

    # Refresh counts of all card states
    def _refresh_stats(self) -> None:
        total, mature, young, unseen, buried, suspended, due = self._query_db()
        new, learning, review = self._get_scheduled_counts()

        self.stats["mature"] = mature // self._config.correction_for_notes
        self.stats["young"] = young // self._config.correction_for_notes
        self.stats["unseen"] = unseen // self._config.correction_for_notes
        self.stats["buried"] = buried // self._config.correction_for_notes
        self.stats["suspended"] = suspended // self._config.correction_for_notes

        self.stats["total"] = total // self._config.correction_for_notes
        self.stats["learned"] = self.stats["mature"] + self.stats["young"]
        self.stats["unlearned"] = self.stats["total"] - self.stats["learned"]

        self.stats["new"] = new
        self.stats["learning"] = learning
        self.stats["review"] = review
        self.stats["due"] = due + self.stats["review"]

        try:
            daysUntilDone: int
            if self._config.learn_per_day == 0:
                daysUntilDone = 0
            else:
                daysUntilDone = math.ceil(
                    self.stats["unseen"] / self._config.learn_per_day
                )
        except Exception as e:
            print(e)
            daysUntilDone: int = 0

        try:
            self.dates["doneDate"] = (
                date.today() + timedelta(days=daysUntilDone)
            ).strftime(self._config.date_format)
        except Exception as e:
            print(e)
            showInfo(
                'Unsupported date format. Defaulting to Day.Month.Year instead. Use one of the shorthands: "us", "asia" or "eu", or specify the date like "\%d.\%m.\%Y", "\%m/\%d/\%Y" etc.\n For more information check the table at: https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior',
                type="warning",
                title="More Overview Stats 2.1 Warning",
            )
            self.dates["doneDate"] = (
                date.today() + timedelta(days=daysUntilDone)
            ).strftime("%d.%m.%Y")

        if daysUntilDone == 1:
            self.dates["daysLeft"] = "{} day".format(daysUntilDone)
        else:
            self.dates["daysLeft"] = "{} days".format(daysUntilDone)

    # Query Anki's db for the current deck's card states
    def _query_db(self) -> List[int]:
        values: List[int] = mw.col.db.first(
            f"""
                select
                -- total
                count(id),
                -- mature
                sum(case when queue = 2 and ivl >= 21
                then 1 else 0 end),
                -- young / learning
                sum(case when queue in (1, 3) or (queue = 2 and ivl < 21)
                then 1 else 0 end),
                -- unseen
                sum(case when queue = 0
                then 1 else 0 end),
                -- buried
                sum(case when queue in (-2, -3)
                then 1 else 0 end),
                -- suspended
                sum(case when queue = -1
                then 1 else 0 end),
                -- due
                sum(case when queue = 1 and due <= ?
                then 1 else 0 end)
                from cards where did in {mw.col.sched._deckLimit():s}
            """,
            round(time.time()),
        )

        # Empty filtered decks can return None => set all values 0
        if None in values:
            values = [0 for x in values]

        return values

    # Get card state counts from Anki's scheduler (new, learning, review)
    def _get_scheduled_counts(self) -> List[int]:
        return list(mw.col.sched.counts())

    # Refresh percentages of all card states
    def _refresh_percentages(self) -> None:
        total: int = self.stats["total"]

        # Avoid division by zero for empty decks
        if total == 0:
            self.percentages = {key: 0.0 for key in self.stats}
        else:
            self.percentages = {
                key: (value / total) for key, value in self.stats.items()
            }

        self.percentages["total"] = 1.0

    # Refresh percentages of all card states ignoring suspended cards
    def _refresh_percentages_without_suspended(self) -> None:
        total_without_suspended: int = self.stats["total"] - self.stats["suspended"]

        # Avoid division by zero for empty decks
        if total_without_suspended == 0:
            self.percentages_without_suspended = {key: 0.0 for key in self.stats}
        else:
            self.percentages_without_suspended = {
                key: (value / total_without_suspended)
                for key, value in self.stats.items()
            }

        self.percentages_without_suspended["total"] = 1.0
