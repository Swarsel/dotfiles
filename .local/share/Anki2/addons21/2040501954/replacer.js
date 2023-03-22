/*
 * Javascript code that performs symbol replacement. insert_symbols.py adds 
 * this script to each Anki editor's WebView after setting the symbol list.
 * 
 * This version is compatible with Anki versions 2.1.41 and newer.
 */

var insert_symbols = new function () {
    const KEY_SPACE = 32;
    const KEY_ENTER = 13;

    var matchList = undefined;
    var shouldCheckOnKeyup = false;

    this.setMatchList = function (str) {
        matchList = JSON.parse(str);
    }

    // Keypress Handling:
    //----------------------------------

    /**
     * During a long press, keydown events are fired repeatedly but keyup is 
     * not fired till the end. Thus, checkForReplacement() should be called 
     * here to make symbol replacement be responsive.
     * 
     * However, the newly entered character does not appear in 
     * focusNode.textContent until later. The new character is accessible via
     * the event object, but the WebView in Anki 2.0 doesn't support evt.key or 
     * evt.code, so figuring out char mappings is complicated for many keys.
     * 
     * Thus, the compromise is to call checkForReplacement() after whitespace
     * during keydown since those char mappings are relatively constant, but
     * defer to keyup for everything else. It works for the most part.
     */
    this.onKeyDown = function (evt) {
        // Disable CTRL commands from triggering replacement:
        if (evt.ctrlKey) {
            return;
        }

        if (evt.which == KEY_SPACE || evt.which == KEY_ENTER) {
            checkForReplacement(evt.currentTarget.getRootNode(), true);
        } else {
            shouldCheckOnKeyup = true;
        }
    }

    this.onKeyUp = function (evt) {
        if (shouldCheckOnKeyup) {
            shouldCheckOnKeyup = false;
            checkForReplacement(evt.currentTarget.getRootNode(), false);
        }
    }

    /**
     * Add event handlers to Editor key events. Setup only needs to be 
     * performed when the editor is first created.
     */

    // For Anki 2.1.41 - 2.1.49
    this.addListenersV1 =  function() {
        forEditorField([], (field) => {
            if (!field.hasAttribute("has-type-symbols")) {
                field.editingArea.editable.addEventListener("keydown", this.onKeyDown)
                field.editingArea.editable.addEventListener("keyup", this.onKeyUp)
                field.setAttribute("has-type-symbols", "")
            }
        })
    }

    // For Anki 2.1.50+
    this.addListenersV2 =  function() {
        setTimeout(() => {
            require("anki/ui").loaded.then(() => {
                fields = require("anki/NoteEditor").instances[0].fields

                for (const field of fields) {
                    field.element.then((fieldElm) => {
                        if (!fieldElm.hasAttribute("has-type-symbols")) {
                            const editingArea = fieldElm.getElementsByClassName("editing-area")[0];
                            const shadowRoot = editingArea.getElementsByClassName("rich-text-editable")[0].shadowRoot;

                            shadowRoot.addEventListener("keydown", this.onKeyDown)
                            shadowRoot.addEventListener("keyup", this.onKeyUp)
                            fieldElm.setAttribute("has-type-symbols", "")
                        }
                    })
                }
            })
        }, 20)  // To prevent our code trying to add listeners before HTML is ready  
    }

    if (typeof forEditorField !== 'undefined') {
        this.addListenersV1();
    } else {
        this.addListenersV2();
    }

    /**
     * Add event handlers to Reviewer key events to extend functionality to
     * "Edit Field During Review" plugin. This needs to be called each time
     * a question/answer is shown since that is when fields are made editable.
     */
    this.setupReviewerKeyEvents = function () {
        $("[contenteditable]").keydown(this.onKeyDown);
        $("[contenteditable]").keyup(this.onKeyUp);
    }

    // Pattern Matching:
    //----------------------------------

    /**
     * Checks whether the current text should be replaced by a symbol from the 
     * symbol list. For simplicity, this function only looks at text within the 
     * current Node.
     */
    function checkForReplacement(root, isWhitespacePressed) {
        var sel = root.getSelection();
        if (sel.isCollapsed) {
            var text = sel.focusNode.textContent;
            var cursorPos = sel.focusOffset;
            //debugDiv(sel.focusNode.textContent);

            var result = matchesKeyword(text, cursorPos, isWhitespacePressed);
            if (result.val !== null) {
                performReplacement(sel.focusNode, cursorPos - result.keylen,
                    cursorPos, result.val, result.html);
            }
        }
    }

    /**
     * Checks whether the substring of TEXT up to END_INDEX matches any keys
     * from the match list. For non-special characters (ie. not colon-delimited
     * and not certain arrows), matching should only occur if both: 
     * - when a whitespace key (space or enter) was pressed.
     * - when the character before the match is a whitespace.
     * See the README for more information.
     *
     * @param text A string containing the substring to check.
     * @param endIndex The length of the substring.
     * @return An object where VAL is value of the matched key-value pair 
     *   (or null if no match), KEYLEN is the length of the key in the 
     *   matched key-value pair, and HTML is whether the value should be 
     *   treated as raw HTML.
     */
    function matchesKeyword(text, endIndex, isWhitespacePressed) {
        for (var i = 0, k; i < matchList.length; i++) {
            triggerOnSpace = (matchList[i].f == 0);

            // Skip entries that trigger only when whitespace is inputted:
            if (triggerOnSpace && !isWhitespacePressed) {
                continue;
            }

            key = matchList[i].key;
            var startIndex = endIndex - key.length;

            // Check if there is a match:
            if (text.substring(startIndex, endIndex) === key) {

                // If indicated, check if char before match is whitespace:
                if (triggerOnSpace && startIndex > 0
                    && !/\s/.test(text[startIndex - 1])) {
                    continue;
                }

                return {
                    "val": matchList[i].val,
                    "keylen": key.length,
                    "html": (matchList[i].f == 2)
                };
            }
        }

        return { "val": null, "keylen": 0, "html": false };
    }

    /**
     * Replaces the text in the given node with new text. Assumes that the node
     * is of type TEXT_NODE.
     * 
     * @param node The node to perform replacement on.
     * @param rangeStart The start index of the range.
     * @param rangeEnd The end index of the range (should be 1 + the index of 
     *   the last character to be deleted). 
     * @param newText Replacement text.
     */
    function performReplacement(node, rangeStart, rangeEnd, newText, isHTML) {
        // Delete key:
        for (var i = rangeStart; i < rangeEnd; i++) {
            document.execCommand("delete", false, null);
        }

        // Insert new symbol:
        command = isHTML ? "insertHTML" : "insertText";
        document.execCommand(command, false, newText);
    }

    // Debugging:
    //----------------------------------

    // $("body").append('<div class="debug1"></div>');
    // $("body").append('<div class="debug2"></div>');

    // $(".debug1").html("Debug #1");
    // $(".debug2").html("Debug #2");

    // function debugDiv1(str) {
    //     $(".debug1").html(str);
    // }

    // function debugDiv2(str) {
    //     $(".debug2").html(str);
    // }
}
