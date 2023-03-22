The configuration options are:

&nbsp;

- **`"Column alignment"`**: Either:
    - `"Start"`: text in column is left aligned (or right aligned for right-to-left scripts)
    - `"Center"`: text in column is center aligned

&nbsp;

- **`"Show internal fields"`**: Boolean (i.e. `true` or `false`). Enable even more columns that map to database fields related to the cards and notes (dev option)

&nbsp;

- **`"Table content"`**: Either:
    - `"No interaction"`: the table content can't be interacted with. This makes the Advanced Browser behave like the regular Anki browser.
    - `"Selectable"`: the table content can be selected. All changes will be ignored. This is useful because this allows you to quickly copy field contents (instead of the regular procedure where you have to do all these steps: select the note, move the mouse to the field, select its content, then copy it).
    - `"Editable"`: Allow to edit some values directly in the table. Not all.

&nbsp;

- **`"Use a single list for fields"`**: Boolean (i.e. `true` or `false`). It controls what is shown in the `fields` menu. If true, every single field of every note type is in the same list. If false, fields will be grouped by note type into sub-menus.
