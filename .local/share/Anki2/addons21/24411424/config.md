### To disable a shortcut, set that shortcut to `<nop>`.

### For macOS users, `Ctrl` is `⌘`, `Alt` is `⌥`, and `Meta` is `^` (control key).


## Editor Options

"editor \_duplicates": Takes functions and binds them to new shortcuts.

This object takes inputs of the form "(function keyword)":"(shortcut)", separated by commas. (e.g. {"editor bold":"Ctrl+Shift+9", "editor cloze":"Alt+Shift+2"})

If you want to set more than one duplicate per shortcut for the reviewer, you can do so by adding the suffix "+++" *immediately* after the shortcut name followed by any distinct string. (e.g. {"editor bold+++ first": "Ctrl+Shift+0", "editor bold+++ 2nd": "Ctrl+Shift+8"})

All the keywords are exactly the same as the keywords used in the json file, making the lines copy-pastable. 

"editor add media": Add external media

"editor add card close window": In the Add Card dialog, closes the given window. For some reason, Macs have a default shortcut for this while all other OSes don't. Since the default is OS dependent, it is given to be `<default>` rather than any specified value.

"editor block indent": Indents the active field. Useful for indenting lists.

"editor block outdent": Outdents (unindents) the active field. Useful for unindenting lists.

"editor bold": Toggle bold 

"editor card layout": Change Card Layout

"editor change col": Change text color

*Note that this shortcut currently exclusively uses the legacy version of color editing. This is incompatible with the new color editing as of Anki 2.1.49. If you don't want to use the old version, disable this shortcut by setting it to <nop>.*

"editor cloze": Insert cloze (increments cloze ID if `Alt` is *not* part of your keybind, so `Ctrl+Shift+C` does increment ID, while `Ctrl+Shift+Alt+C` does not)

"editor cloze alt": Insert cloze (behaves identically to "editor cloze")

"editor cloze forced increment": Insert cloze, **always increments the cloze ID number**, *does not activate cloze add-ons*

"editor cloze no increment": Insert cloze, **never increments the cloze ID number**, *does not activate cloze add-ons*

The reason for the seemingly weird editor cloze behavior is Anki's internal implementation of the cloze insertion shortcuts. Anki's implementation is used in "editor cloze" and "editor cloze alt" and should play well with other addons, while a different implementation is used for "forced increment" and "no increment".

"editor change note type": Change the type of the given note

"editor confirm add card": In the add card editing window, adds the card

"editor focus tags": Switch focus to the Tags field

"editor foreground": Set foreground color

*Note that this shortcut currently exclusively uses the legacy version of color editing. This is incompatible with the new color editing as of Anki 2.1.49. If you don't want to use the old version, disable this shortcut by setting it to <nop>.*

"editor html edit": Edit the card's HTML

"editor insert latex": Insert LaTeX formatted text

"editor insert latex equation": Insert a LaTeX equation

"editor insert latex math environment": Insert a LaTeX math environment

"editor insert mathjax block": Insert a MathJax block

"editor insert mathjax chemistry": Insert a chemistry thing in MathJax

"editor insert mathjax inline": Insert an inline MathJax expresesion

"editor list insert ordered": Put an ordered list into the active field.
k
"editor list insert unordered": Put an unordered list into the active field.

"editor italic": Toggle italics

"editor record sound": Record sound

"editor remove format": Remove card formatting

"editor subscript": Toggle subscript

"editor superscript": Toggle superscript

"editor toggle sticky all": *Anki 2.1.45+* Toggle the stickiness of all fields. "Toggle all" is interpreted the same was as in vanilla Anki: If any field is sticky, turn all stickies off. Otherwise, turn all stickies on.

"editor toggle sticky current": *Anki 2.1.45+* Toggle the stickiness of the current field.

*In the current implementation for toggling stickies, setting this to something other than the default will lose you the ability to click to toggle the sticky pins. If you want to retain this ability, using a duplicate `"editor toggle sticky current"` will still allow you to click pins.*

"editor underline": Toggle underline

**In the future, these shortcuts may be removed and put into a new add-on, as they are not part of Anki's default functionality.**

Within "editor \_extras":

"paste custom text": Pastes a custom piece of html text into a card field (defined in "Ω custom paste text")

"editor \_pastes": Same functionality as paste custom text, but allows any number of texts with any label (texts are defined in "Ω custom paste extra texts", labels must match)

e.g. `"editor _pastes": {"dashes":"Ctrl+Shift+5", "dots":"Ctrl+Shift+6"}` matched with `"Ω custom paste extra texts": {"dashes":"<b>--</b>","dots":". . ."}` pastes the corresponding text with the corresponding label

## Main Toolbox Options

"m\_toolbox \_duplicates": Takes functions and binds them to new shortcuts.

This object takes inputs of the form "(function keyword)":"(shortcut)", separated by commas. (e.g. {"m\_toolbox undo":"u","m\_toolbox study":"9"})

All the keywords are exactly the same as the keywords used in the json file, making the lines copy-pastable. 

If you want to set more than one duplicate per shortcut for the reviewer, you can do so by adding the suffix "+++" *immediately* after the shortcut name followed by any distinct string. (e.g. {"m\_toolbox study+++ first": "6", "m\_toolbox study+++ 2nd": "V"})

"m_toolbox addons": Go to the addons window

"m_toolbox create filtered deck": Create a filtered deck

"m_toolbox export": Export the user's decks

"m_toolbox import": Import a deck file (.apkg, etc.)

"m_toolbox preferences": Go to the user preferences window

"m_toolbox quit": Quit Anki

"m_toolbox see documentation": Go to the Anki manual

"m_toolbox study": Start studying the selected deck

"m_toolbox switch profile": Switch user profiles

"m_toolbox undo": Undo the **last main window (reviewer)** action

## Home Options

**NOTE: Setting these to "Ctrl+:", "d", "s", "a", "b", "t", or "y" will not work if they are not the default setting for that function.**

"main add": Add new card

"main browse": Enter card browser

"main debug": Open debug screen

"main deckbrowser": Go back to home screen

"main stats": Enter stats screen

"main study": Study current deck

"main sync": Synchronize with AnkiWeb

## Reviewer Options

"reviewer \_duplicates": Takes functions and binds them to new shortcuts.

This object takes inputs of the form "(function keyword)":"(shortcut)", separated by commas. (e.g. {"reviewer mark card":"]","reviewer flip card 1":"-"})

All the keywords are exactly the same as the keywords used in the json file, making the lines copy-pastable. (Those who want to remove the numbers from stuff like "reviewer flip card" can do so as well)

If you want to set more than one duplicate per shortcut for the reviewer, you can do so by adding the suffix "+++" *immediately* after the shortcut name followed by any distinct string. (e.g. {"reviewer flip card 3+++ first": "l", "reviewer flip card 3+++ 2nd": "t"})

**Make sure to remap keys to empty keyspace.**

"reviewer bury card": Bury this card

"reviewer bury note": Bury this note (card and associated cards)

"reviewer card info": Display info about this card

"reviewer choice [1234]": Select 1/2/3/4 (Again/Hard/Good/Easy or Again/Good/Easy)

"reviewer delete note": Delete this note

"reviewer edit current": Edit the card currently being reviewed

"reviewer flip card [123]": Flip the card to see the answer

"reviewer mark card": Mark this card with a star

"reviewer more options": Display the menu showing other review options for this card (e.g. flagging the card, suspend/delete/bury, playing audio, etc.)

"reviewer options menu": Go to the review options menu

"reviewer pause audio": Pause the audio being played

"reviewer play recorded voice": If there is a recorded voice, play it

"reviewer previous card info": Display info about the previous card

"reviewer record voice": Record your voice

"reviewer replay audio [12]": Replay audio attached to the card

"reviewer set due date": Reschedules a card in the review schedule in Anki 2.1.41+

"reviewer set flag [12345670]": Set a flag on this card (or none for 0), changing colors depending on the number (1/2/3/4, and for 2.1.45+, 5/6/7 as well)

"reviewer seek backward": Rewind the audio 5 seconds

"reviewer seek forward": More the audio forward 5 seconds

"reviewer suspend card": Suspend this card

"reviewer suspend note": Suspend this note

## Browser Window Options

"window\_browser \_filters": Auto-fills the search bar of the browser with the given text. Can be used for filters such as current deck (`deck:current`) or cards due for review (`is:due`)

The syntax for this is: `"(filter name): (shortcut)"`, though one may need to escape quotes with `\` e.g. `"deck: Something something"` becomes `\"deck: Something something\"`

Sub-objects within `_filters`: 

"\_concat": Instead of replacing text in the search bar, adds the text to the end of the search bar

"\_orConcat": Adds the "or" + the text to the end of the search bar ("or" acts like logical or for searches)

"window_browser add card": Adds a new card (goes to the add window)

"window_browser add tag": Adds a tag to the selected card

"window_browser change deck": Changes the deck of the selected card

"window_browser change note type": Changes the note type of the selected card

"window_browser clear flags": Removes all flags from a card

"window_browser clear unused tags": *Not in vanilla Anki*, Removes all unused tags

"window_browser close": Closes the browser

"window_browser delete": Deletes the selected card

"window_browser filter": Adds filters to a search

"window_browser find": Finds a pattern

"window_browser find duplicates": *Not in vanilla Anki*, Finds cards with the same fields

"window_browser find and replace": Finds a pattern and replaces it with another pattern

"window_browser first card": Selects only the first card in the list

"window_browser flag_blue": Toggles the blue flag

"window_browser flag_green": Toggles the green flag

"window_browser flag_purple": Toggles the purple flag

"window_browser flag_red": Toggles the red flag

"window_browser forget card": Forgets the selected card (sets the card as new)

"window_browser goto card list": Switches focus to the card list

"window_browser goto next note": Selects the note after the selected note in the list

"window_browser goto note": Switches focus to the note fields

"window_browser goto previous note": Selects the note before the selected note

"window_browser goto sidebar": Goes to the sidebar of decks/note types

"window_browser guide": Opens the browser guide in the default browser

"window_browser info": Shows info of the selected card

"window_browser invert selection": Inverts the selection of cards

"window_browser last card": Goes to the last card on the list

"window_browser manage note types": *Not in vanilla Anki*, Goes to the note type management window

"window_browser preview": Emulates what the card will look like during review

"window_browser remove current filter": *Not in vanilla Anki*, Removes the most recently used filter previously saved to the sidebar

"window_browser remove tag": Removes tags from a card

"window_browser reposition": Repositions a new card in the new card queue

"window_browser reschedule": Reschedules a card in the review schedule, named "set due date" in Anki 2.1.41+

"window_browser save current filter": *Not in vanilla Anki*, Saves the current filter to the sidebar (and lets you name it)

"window_browser select all": Selects all cards

"window_browser select notes": *Not in vanilla Anki*, Selects only the current notes

"window_browser sidebar search": *Useful only in Anki 2.1.45+* Sets the sidebar to initialize a search of the selected item in the sidebar

"window_browser sidebar select": *Useful only in Anki 2.1.45+* Sets the sidebar to just select the item in the sidebar

"window_browser suspend": Suspends the selected cards

"window_browser toggle mark": Toggles the mark on the selected cards

"window_browser undo": Undoes the latest **browser** action (**m\_toolbox undo** undoes **reviewer** actions)

## Add-on Preferences

**These options are for changing a few settings on the add-on itself.**

"Ω custom paste end style": For the exceptionally lazy (like me). If set to "y", inserts a `</span>` and a zero-width space at the end of the custom text to stop the custom style from bleeding into new text.

Otherwise, the custom paste will behave exactly like regular paste.

"Ω custom paste text": Controls what html will be pasted by "custom paste" in "editor \_extras"	
e.g. `"Ω custom paste text": "<span style=\"font-size: 20px; color:#3399ff\">◆</span>"`

"Ω custom paste extra texts": Controls what html will be pasted by the correspondingly labeled paste in "editor \_pastes" (See "editor \_pastes" for an example)

"Ω enable main/window_browser/editor/etc.": If set to "n", doesn't enable the corresponding set of shortcuts for the respective functions (useful for addon compatability in a pinch)

"Ω enable conflict warning": If set to "y", shows a warning window whenever two shortcuts of the same type are set to the same key.
