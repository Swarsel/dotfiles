from .config import AddonConfig
from .data import DeckData
from aqt import mw


class Table:
    """The Table object assembles the overview table html.

    Parameters
    ----------
    config : AddonConfig
        Object used to load the addon's user configuration.
    deck_data : DeckData
        Object used to load the currently active deck's data.
    """

    def __init__(self, config: AddonConfig, deck_data: DeckData) -> None:
        self._config: AddonConfig = config
        self._deck_data: DeckData = deck_data

    def get_html(self) -> str:
        """Assemble the complete overview table in HTML code.

        The table contains additional stats and a "Study Now" button for
        unfinished decks. For finished decks the deck name is added above
        the table. Additional options can be set using the `AddonConfig`
        object.

        Returns
        -------
        str
            HTML code of the assembled overview table.
        """

        return f"""
        {self._get_style()}
        {self._get_start()}
        {self._get_study_stats()}
        {self._get_deck_stats()}
        {self._get_end()}
        """

    # Return the table's style css
    def _get_style(self) -> str:
        return (
            """
            <style type="text/css">
            <!--
            hr {
                height: 1px;
                border: none;
                border-top: 1px solid #aaa;
            }

            td {
                vertical-align: top;
            }

            td.col1 {
                text-align: left;
            }

            td.col2 {
                text-align: right;
                padding-left: 1.2em;
                padding-right: 1.2em;
            }

            td.col3 {
                text-align: left;
                padding-left: 1.2em;
                padding-right: 1.2em;
            }

            td.col4 {
                text-align: right;
            }

            td.new {
                font-weight: bold;
                color: """
            + self._config.stat_colors["New"]
            + """;
            }

            td.learning {
                font-weight: bold;
                color: """
            + self._config.stat_colors["Learning"]
            + """;
            }

            td.review {
                font-weight: bold;
                color: """
            + self._config.stat_colors["Review"]
            + """;
            }

            td.percent {
                font-weight: normal;
                color: """
            + self._config.stat_colors["Percent"]
            + """;
            }

            td.mature {
                font-weight: normal;
                color: """
            + self._config.stat_colors["Mature"]
            + """;
            }

            td.young {
                font-weight: normal;
                color: """
            + self._config.stat_colors["Young"]
            + """;
            }

            td.learned {
                font-weight: normal;
                color: """
            + self._config.stat_colors["Learned"]
            + """;
            }

            td.unseen {
                font-weight: normal;
                color: """
            + self._config.stat_colors["Unseen"]
            + """;
            }

            td.suspended {
                font-weight: normal;
                color: """
            + self._config.stat_colors["Suspended"]
            + """;
            }

            td.buried {
                font-weight: normal;
                color: """
            + self._config.stat_colors["Buried"]
            + """;
            }

            td.doneDate {
                font-weight: bold;
                color: """
            + self._config.stat_colors["Done on Date"]
            + """;
            }

            td.daysLeft {
                font-weight: bold;
                color: """
            + self._config.stat_colors["Days until done"]
            + """;
            }

            td.total {
                font-weight: bold;
                color: """
            + self._config.stat_colors["Total"]
            + """;
            }
            -->
            </style>"""
        )

    # Return start of the table's HTML
    def _get_start(self) -> str:
        return f"""
        {self._get_deck_name()}
        <table cellspacing="2">
        """

    # Return HTML of the deck name for unfinished decks
    def _get_deck_name(self) -> str:
        if not self._deck_data.is_finished():
            return ""

        deck_name: str = mw.col.decks.current()["name"]

        return f"""
        <center>
        <h3>{deck_name}</h3>
        """

    # Return HTML of the study stats for unfinished decks
    def _get_study_stats(self) -> str:
        if self._deck_data.is_finished():
            return ""

        return """
        <tr>
            <td class="col1">{labels[new]:s}</td>
            <td class="col2 new">{deck_stats[new]:d}</td>
            <td class="col3 percent">{deck_percentages[new]:.0%}</td>
            <td class="col4 percent">{deck_percentages_without_suspended[new]:.0%}</td>
        </tr>
        <tr>
            <td class="col1">{labels[learning]:s}</td>
            <td class="col2 learning">{deck_stats[learning]:d}</td>
            <td class="col3 percent">{deck_percentages[learning]:.0%}</td>
            <td class="col4 percent">{deck_percentages_without_suspended[learning]:.0%}</td>
        </tr>
        <tr>
            <td class="col1">{labels[review]:s}</td>
            <td class="col2 review">{deck_stats[review]:d}</td>
            <td class="col3 percent">{deck_percentages[review]:.0%}</td>
            <td class="col4 percent">{deck_percentages_without_suspended[review]:.0%}</td>
        </tr>
        <tr>
            <td colspan="4"><hr /></td>
        </tr>
        """.format(
            labels=self._deck_data.labels,
            deck_stats=self._deck_data.stats,
            deck_percentages=self._deck_data.percentages,
            deck_percentages_without_suspended=self._deck_data.percentages_without_suspended,
        )

    # Return HTML of the deck stats for unfinished decks
    def _get_deck_stats(self) -> str:
        return """
        <tr>
            <td class="col1">{labels[mature]:s}</td>
            <td class="col2 mature">{deck_stats[mature]:d}</td>
            <td class="col3 percent">{deck_percentages[mature]:.0%}</td>
            <td class="col4 percent">{deck_percentages_without_suspended[mature]:.0%}</td>
        </tr>
        <tr>
            <td class="col1">{labels[young]:s}</td>
            <td class="col2 young">{deck_stats[young]:d}</td>
            <td class="col3 percent">{deck_percentages[young]:.0%}</td>
            <td class="col4 percent">{deck_percentages_without_suspended[young]:.0%}</td>
        </tr>
        <tr>
            <td colspan="4"><hr /></td>
        </tr>
        <tr>
            <td class="col1">{labels[learned]:s}</td>
            <td class="col2 learned">{deck_stats[learned]:d}</td>
            <td class="col3 percent">{deck_percentages[learned]:.0%}</td>
            <td class="col4 percent">{deck_percentages_without_suspended[learned]:.0%}</td>
        </tr>
        <tr>
            <td class="col1">{labels[unseen]:s}</td>
            <td class="col2 unseen">{deck_stats[unseen]:d}</td>
            <td class="col3 percent">{deck_percentages[unseen]:.0%}</td>
            <td class="col4 percent">{deck_percentages_without_suspended[unseen]:.0%}</td>
        </tr>
        <tr>
            <td class="col1">{labels[buried]:s}</td>
            <td class="col2 buried">{deck_stats[buried]:d}</td>
            <td class="col3 percent">{deck_percentages[buried]:.0%}</td>
            <td class="col4 percent">{deck_percentages_without_suspended[buried]:.0%}</td>
        </tr>
        <tr>
            <td class="col1">{labels[suspended]:s}</td>
            <td class="col2 suspended">{deck_stats[suspended]:d}</td>
            <td class="col3 percent">{deck_percentages[suspended]:.0%}</td>
            <td class="col4 percent">ignored</td>
        </tr>
        <tr>
            <td colspan="4"><hr /></td>
        </tr>
        <tr>
            <td class="col1">{labels[total]:s}</td>
            <td class="col2 total">{deck_stats[total]:d}</td>
            <td class="col3 percent">{deck_percentages[total]:.0%}</td>
            <td class="col4 percent">{deck_percentages_without_suspended[total]:.0%}</td>
        </tr>
            <td colspan="4"><hr /></td>
        <tr>
            <td class="col1">{labels[doneDate]:s}</td>
            <td class="col2 daysLeft">{deck_dates[daysLeft]:s}</td>
            <td class="col3">on:</td>
            <td class="col4 doneDate">{deck_dates[doneDate]:s}</td>
        </tr>
        """.format(
            labels=self._deck_data.labels,
            deck_stats=self._deck_data.stats,
            deck_dates=self._deck_data.dates,
            deck_percentages=self._deck_data.percentages,
            deck_percentages_without_suspended=self._deck_data.percentages_without_suspended,
        )

    # Return end of the table's HTML
    def _get_end(self):
        return f"""
            {self._get_study_button()}
        </table>
        </br>
        """

    # Return HTML of the study button for unfinished decks
    def _get_study_button(self) -> str:
        if self._deck_data.is_finished():
            return ""

        return f"""
        <tr>
            <td colspan="4" style="text-align: center; padding-top: 0.6em;">{mw.button("study", "Study Now", id="study", extra="autofocus")}</td>
        </tr>
        """
