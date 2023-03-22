;; The default is 800 kilobytes.  Measured in bytes.
(setq gc-cons-threshold (* 50 1000 1000))

;; Profile emacs startup
(add-hook 'emacs-startup-hook
          (lambda ()
            (message "*** Emacs loaded in %s with %d garbage collections."
                     (format "%.2f seconds"
                             (float-time
                              (time-subtract after-init-time before-init-time)))
                     gcs-done)))

;; use UTF-8 everywhere
      (set-language-environment "UTF-8")
      ;; set default font size
      (if (memq system-type '(windows-nt ms-dos))
        (defvar swarsel/default-font-size 100))
      (if (memq system-type '(gnu/linux))
          (defvar swarsel/default-font-size 130))

;; set Nextcloud directory for journals etc.
      (setq swarsel-sync-directory "~/Nextcloud")

      ;; set default directory to HOME (on windows, set HOME system variable to "C:\Users\USERNAME")
      (setq swarsel-home-directory "~/")

      ;; set emacs directory
      (setq swarsel-emacs-directory "~/.emacs.d")
      (setq swarsel-init-el-filepath (expand-file-name "init.el" swarsel-emacs-directory))
      (setq swarsel-emacs-org-filepath (expand-file-name "Emacs.org" swarsel-emacs-directory))
      (setq swarsel-sway-config-filepath "~/.config/sway/config")

            ;; set git/project directory
      (if (memq system-type '(windows-nt ms-dos))
          (setq swarsel-projects-directory "~/Projects"))
      (if (memq system-type '(gnu/linux))
          (setq swarsel-projects-directory "~/Documents/GitHub"))

      ;; set Emacs main configuration .org names
      (setq swarsel-emacs-org-file "Emacs.org")
      (setq swarsel-anki-org-file "Anki.org")
      (setq swarsel-tasks-org-file "Tasks.org")
      (setq swarsel-archive-org-file "Archive.org")
      (setq swarsel-journal-org-file "Journal.org")
      (setq swarsel-org-folder-name "org")
      (setq swarsel-obsidian-daily-folder-name "daily")
      (setq swarsel-obsidian-folder-name "Obsidian")
      (setq swarsel-obsidian-vault-name "Main")

      (setq swarsel-standard-font "Fira Code Retina")
      (setq swarsel-alt-font "Cantarell")

      ;; set directory paths
      (setq swarsel-org-directory (expand-file-name swarsel-org-folder-name  swarsel-sync-directory)) ; path to org folder
      (setq swarsel-obsidian-directory (expand-file-name swarsel-obsidian-folder-name swarsel-sync-directory)) ; path to obsidian
      (setq swarsel-obsidian-vault-directory (expand-file-name swarsel-obsidian-vault-name swarsel-obsidian-directory)) ; path to obsidian vault
      (setq swarsel-obsidian-daily-directory (expand-file-name swarsel-obsidian-daily-folder-name swarsel-obsidian-vault-directory)) ; path to obsidian daily folder

      ;; filepaths to certain documents
      (setq swarsel-org-anki-filepath (expand-file-name swarsel-anki-org-file swarsel-org-directory)) ; path to anki export file
      (setq swarsel-org-tasks-filepath (expand-file-name swarsel-tasks-org-file swarsel-org-directory))
      (setq swarsel-org-archive-filepath (expand-file-name swarsel-archive-org-file swarsel-org-directory))
      (setq swarsel-org-journal-filepath (expand-file-name swarsel-journal-org-file swarsel-org-directory))

;; set paths to authentication files (forge)
      (setq auth-sources '("~/.emacs.d/.authinfo.gpg")
            auth-source-cache-expiry nil) ; default is 2h

    ;; set pandoc for markdown compilation
      (setq markdown-command "pandoc") 
      (if (memq system-type '(windows-nt ms-dos))
        (setq pandoc-binary "C:/Program Files/Pandoc"
              epg-gpg-home-directory "C:/Program Files (x86)/GnuPG"
              epg-gpg-program (concat epg-gpg-home-directory "/bin/gpg.exe")
              epg-gpgconf-program  (concat epg-gpg-home-directory "/bin/gpgconf.exe")))

;; Initialize package sources
(require 'package)

(setq package-archives '(("melpa" . "https://melpa.org/packages/")
                         ("org" . "https://orgmode.org/elpa/")
                         ("elpa" . "https://elpa.gnu.org/packages/")))

;; Initialize package system
(package-initialize)
;; If this is present, we need to check if we already have packages cloned
(unless package-archive-contents
  ;; ...so refresh package list
 (package-refresh-contents))

;; Initialize use-package on non-Linux platforms
(unless (package-installed-p 'use-package)
   (package-install 'use-package))

(require 'use-package)
;; It doesn't ensure packages download is on by default.
;; This makes sure it tries to download it
(setq use-package-always-ensure t)

;; Change the user-emacs-directory to keep unwanted things out of ~/.emacs.d
(setq user-emacs-directory (expand-file-name "~/.cache/emacs/")
      url-history-file (expand-file-name "url/history" user-emacs-directory))

;; Use no-littering to automatically set common paths to the new user-emacs-directory
(use-package no-littering)

;; Keep customization settings in a temporary file (thanks Ambrevar!)
(setq custom-file
      (if (boundp 'server-socket-dir)
          (expand-file-name "custom.el" server-socket-dir)
        (expand-file-name (format "emacs-custom-%s.el" (user-uid)) temporary-file-directory)))
(load custom-file t)

;; Make ESC quit prompts
  (global-set-key (kbd "<escape>") 'keyboard-escape-quit)

  ;; Set up general keybindings
  (use-package general
    :config
    (general-create-definer swarsel/leader-keys
      :keymaps '(normal insert visual emacs)
      :prefix "SPC"
      :global-prefix "C-SPC")

    (swarsel/leader-keys
      "t"  '(:ignore t :which-key "toggles")
      "tt" '(counsel-load-theme :which-key "choose theme")
      "c"  '(:ignore c :which-key "capture")
      "cj" '((lambda () (interactive) (org-capture nil "jj")) :which-key "journal")
      "l"  '(:ignore l :which-key "links")
      "li" '((lambda () (interactive) (find-file swarsel-init-el-filepath)) :which-key "init.el")
      "le" '((lambda () (interactive) (find-file swarsel-emacs-org-filepath)) :which-key "Emacs.org")
      "lo" '(dired swarsel-obsidian-vault-directory :which-key "obsidian") 

      "la" '((lambda () (interactive) (find-file swarsel-org-anki-filepath)) :which-key "anki")
      "ls" '((lambda () (interactive) (find-file swarsel-sway-config-filepath)) :which-key "sway config")
      )
    )

    ;; General often used hotkeys
  (general-define-key
   "C-M-a" (lambda () (interactive) (org-capture nil "a")) ; make new anki card
   "C-M-d" 'swarsel-obsidian-daily ; open daily obsidian file and create if not exist
   "C-M-S" 'swarsel-anki-set-deck-and-notetype ; switch deck and notetye for new anki cards
   "C-M-s" 'markdown-download-screenshot ; wrapper for org-download-screenshot
   )

;; Emulate vim in emacs
(use-package evil
  :init
  (setq evil-want-integration t) ; loads evil
  (setq evil-want-keybinding nil) ; loads "helpful bindings" for other modes
  (setq evil-want-C-u-scroll t) ; scrolling using C-u
  (setq evil-want-C-i-jump nil) ; jumping with C-i
  :config
  (evil-mode 1)
  (define-key evil-insert-state-map (kbd "C-g") 'evil-normal-state) ; alternative for exiting insert mode
  (define-key evil-insert-state-map (kbd "C-h") 'evil-delete-backward-char-and-join) ; dont show help but instead do normal vim delete backwards

  ;; Use visual line motions even outside of visual-line-mode buffers
  (evil-global-set-key 'motion "j" 'evil-next-visual-line)
  (evil-global-set-key 'motion "k" 'evil-previous-visual-line)

  ;; Don't use evil-mode in these contexts
  (evil-set-initial-state 'messages-buffer-mode 'normal)
  (evil-set-initial-state 'dashboard-mode 'normal)
  (evil-set-initial-state 'python-inferior-mode 'normal)
  (add-hook 'org-capture-mode-hook 'evil-insert-state))
;; Evil-configuration for different modes
(use-package evil-collection
  :after evil
  :config
  (evil-collection-init))

(setq inhibit-startup-message t)

    (scroll-bar-mode -1)        ; Disable visible scrollbar
    (tool-bar-mode -1)          ; Disable the toolbar
    (tooltip-mode -1)           ; Disable tooltips
    (set-fringe-mode 10)        ; Give some breathing room

    (menu-bar-mode -1)            ; Disable the menu bar

    ;; Set up the visible bell
    (setq visible-bell nil)

    ;; Increase undo limit
    (setq undo-limit 80000000
          evil-want-fine-undo t
          auto-save-default t
          password-cach-expiry nil
          scroll-margin 2)

    (display-time-mode 1)

  (unless (string-match-p "^Power N/A" (battery))   ; On laptops...
  (display-battery-mode 1))                       ; it's nice to know how much power you have

(global-subword-mode 1)                           ; Iterate through CamelCase words

  (setq mouse-wheel-scroll-amount '(1 ((shift) . 1))) ;; one line at a time
  (setq mouse-wheel-progressive-speed nil) ;; don't accelerate scrolling
  (setq mouse-wheel-follow-mouse 't) ;; scroll window under mouse
    ;; Generally show line numbers
    (column-number-mode)
    ;; (global-display-line-numbers-mode t)

    ;; ;; Disable line numbers for some modes
    ;; (dolist (mode '(org-mode-hook
    ;;                 treemacs-mode-hook
    ;;                 term-mode-hook
    ;;                  shell-mode-hook
    ;;                 eshell-mode-hook))
    ;;     (add-hook mode (lambda () (display-line-numbers-mode 0))))

    ;; Enable line numbers for some modes
  (dolist (mode '(text-mode-hook
                  prog-mode-hook
                  conf-mode-hook))
    (add-hook mode (lambda () (display-line-numbers-mode 1))))

  ;; Override some modes which derive from the above
  (dolist (mode '(org-mode-hook))
    (add-hook mode (lambda () (display-line-numbers-mode 0))))

(set-face-attribute 'default nil :font swarsel-standard-font :height swarsel/default-font-size)
;; Set the fixed pitch face
(set-face-attribute 'fixed-pitch nil :font swarsel-standard-font  :height 140)
;; Set the variable pitch face
(set-face-attribute 'variable-pitch nil :font swarsel-alt-font :height 120 :weight 'regular)

(defun swarsel/replace-unicode-font-mapping (block-name old-font new-font)
  (let* ((block-idx (cl-position-if
                         (lambda (i) (string-equal (car i) block-name))
                         unicode-fonts-block-font-mapping))
         (block-fonts (cadr (nth block-idx unicode-fonts-block-font-mapping)))
         (updated-block (cl-substitute new-font old-font block-fonts :test 'string-equal)))
    (setf (cdr (nth block-idx unicode-fonts-block-font-mapping))
          `(,updated-block))))

(use-package unicode-fonts
  :custom
  (unicode-fonts-skip-font-groups '(low-quality-glyphs))
  :config
  ;; Fix the font mappings to use the right emoji font
  (mapcar
    (lambda (block-name)
      (swarsel/replace-unicode-font-mapping block-name "Apple Color Emoji" "Noto Color Emoji"))
    '("Dingbats"
      "Emoticons"
      "Miscellaneous Symbols and Pictographs"
      "Transport and Map Symbols"))
  (unicode-fonts-setup))

(use-package emojify
  :hook (erc-mode . emojify-mode)
  :commands emojify-mode)

(use-package doom-themes
:init (load-theme 'doom-city-lights t))

;; Dependency of doom-modeline
;; Install using M-x all-the-icons-install-fonts
(use-package all-the-icons
  :if (display-graphic-p))

;; Adds a more beautiful modeline with less clutter
(use-package doom-modeline
  :init (doom-modeline-mode 1)
  :custom ((doom-modeline-height 30)))

(use-package which-key
  :init (which-key-mode)
  :diminish which-key-mode
  :config
  (setq which-key-idle-delay 0.3))

(use-package ivy
  :diminish
  :bind (("C-s" . swiper)  ; call swiper (find tool)
         :map ivy-minibuffer-map 
                                        ;("TAB" . ivy-alt-done)	; autocomplete
         ("C-l" . ivy-alt-done)
         ("C-j" . ivy-next-line) ; go up and down in ivy using vim keys
         ("C-k" . ivy-previous-line)
         :map ivy-switch-buffer-map
         ("C-k" . ivy-previous-line)
         ("C-l" . ivy-done)
         ("C-d" . ivy-switch-buffer-kill)
         :map ivy-reverse-i-search-map
         ("C-k" . ivy-previous-line)
         ("C-d" . ivy-reverse-i-search-kill)))

;; Enable ivy everywhere
(ivy-mode 1)
;; Basic interface
(setq ivy-use-virtual-buffers t)
(setq ivy-count-format "(%d/%d) ")

;; More information about functions in ivy-mode
(use-package ivy-rich
  :init
  (ivy-rich-mode 1))

(use-package counsel
  :bind (("C-M-j" . counsel-switch-buffer)
          ("M-x" . counsel-M-x)
          ("C-x b" . counsel-ibuffer)
          ("C-x C-f" . counsel-find-file)
          :map minibuffer-local-map
          ("C-r" . 'counsel-minibuffer-history))
  :config
  (setq ivy-initial-inputs-alist nil))
  (counsel-mode 1)

(use-package helpful
  :custom
  (counsel-describe-function-function #'helpful-callable)
  (counsel-describe-variable-function #'helpful-variable)
  :bind
  ([remap describe-function] . counsel-describe-function)
  ([remap describe-command] . helpful-command)
  ([remap describe-variable] . counsel-describe-variable)
  ([remap describe-key] . helpful-key))

(use-package hydra)

  ;; change the text size of the current buffer
(defhydra hydra-text-scale (:timeout 4)
  "scale text"
  ("j" text-scale-increase "in")
  ("k" text-scale-decrease "out")
  ("f" nil "finished" :exit t))

(swarsel/leader-keys
  "ts" '(hydra-text-scale/body :which-key "scale text"))

(set-frame-parameter (selected-frame) 'alpha '(95 . 95))
(add-to-list 'default-frame-alist '(alpha . (95 . 95)))
(set-frame-parameter (selected-frame) 'fullscreen 'maximized)
(add-to-list 'default-frame-alist '(fullscreen . maximized))

(defun swarsel/org-mode-setup ()
  (org-indent-mode)
  (variable-pitch-mode 1)
                                        ;(auto-fill-mode 0)
  (visual-line-mode 1))
                                        ;(setq evil-auto indent nil)
                                        ;(diminish org-indent-mode)

(use-package org
  :hook (org-mode . swarsel/org-mode-setup)
  :config
  (setq org-ellipsis " ▾"
        org-hide-emphasis-markers t)
  (setq org-startup-folded t)
  (setq org-support-shift-select t)
  (setq org-agenda-start-with-log-mode t)
  (setq org-log-done 'time)
  (setq org-log-into-drawer t)
  (setq org-startup-with-inline-images t)
  (setq org-format-latex-options '(:foreground "White" :background default :scale 2.0 :html-foreground "Black" :html-background "Transparent" :html-scale 1.0 :matchers ("begin" "$1" "$" "$$" "\\(" "\\[")))

  (setq org-agenda-files
        '(swarsel-org-tasks-filepath
          swarsel-org-archive-filepath
          swarsel-org-anki-filepath))

  (require 'org-habit)
  (add-to-list 'org-modules 'org-habit)
  (setq org-habit-graph-column 60)

  (setq org-todo-keywords
        '((sequence "TODO(t)" "NEXT(n)" "|" "DONE(d!)")
          (sequence "BACKLOG(b)" "PLAN(p)" "READY(r)" "ACTIVE(a)" "REVIEW(v)" "WAIT(w@/!)" "HOLD(h)" "|" "COMPLETED(c)" "CANC(k@)")))

  (setq org-refile-targets
        '((swarsel-archive-org-file :maxlevel . 1)
          (swarsel-anki-org-file :maxlevel . 1)
          (swarsel-tasks-org-file :maxlevel . 1)))

  ;; Configure custom agenda views
  (setq org-agenda-custom-commands
        '(("d" "Dashboard"
           ((agenda "" ((org-deadline-warning-days 7)))
            (todo "NEXT"
                  ((org-agenda-overriding-header "Next Tasks")))
            (tags-todo "agenda/ACTIVE" ((org-agenda-overriding-header "Active Projects")))))

          ("n" "Next Tasks"
           ((todo "NEXT"
                  ((org-agenda-overriding-header "Next Tasks")))))

          ("W" "Work Tasks" tags-todo "+work-email")

          ;; Low-effort next actions
          ("e" tags-todo "+TODO=\"NEXT\"+Effort<15&+Effort>0"
           ((org-agenda-overriding-header "Low Effort Tasks")
            (org-agenda-max-todos 20)
            (org-agenda-files org-agenda-files)))

          ("w" "Workflow Status"
           ((todo "WAIT"
                  ((org-agenda-overriding-header "Waiting on External")
                   (org-agenda-files org-agenda-files)))
            (todo "REVIEW"
                  ((org-agenda-overriding-header "In Review")
                   (org-agenda-files org-agenda-files)))
            (todo "PLAN"
                  ((org-agenda-overriding-header "In Planning")
                   (org-agenda-todo-list-sublevels nil)
                   (org-agenda-files org-agenda-files)))
            (todo "BACKLOG"
                  ((org-agenda-overriding-header "Project Backlog")
                   (org-agenda-todo-list-sublevels nil)
                   (org-agenda-files org-agenda-files)))
            (todo "READY"
                  ((org-agenda-overriding-header "Ready for Work")
                   (org-agenda-files org-agenda-files)))
            (todo "ACTIVE"
                  ((org-agenda-overriding-header "Active Projects")
                   (org-agenda-files org-agenda-files)))
            (todo "COMPLETED"
                  ((org-agenda-overriding-header "Completed Projects")
                   (org-agenda-files org-agenda-files)))
            (todo "CANC"
                  ((org-agenda-overriding-header "Cancelled Projects")
                   (org-agenda-files org-agenda-files)))))))

  (setq org-capture-templates
        `(
          ("a" "Anki basic"
           entry
           (file+headline swarsel-org-anki-filepath "Dispatch")
           (function swarsel-anki-make-template-string))

          ("A" "Anki cloze"
           entry
           (file+headline org-swarsel-anki-file "Dispatch")
           "* %<%H:%M>\n:PROPERTIES:\n:ANKI_NOTE_TYPE: Cloze\n:ANKI_DECK: 🦁 All::01 ❤️ Various::00 ✨ Allgemein\n:END:\n** Text\n%?\n** Extra\n")
          ("t" "Tasks / Projects")
          ("tt" "Task" entry (file+olp swarsel-org-tasks-filepath "Inbox")
           "* TODO %?\n  %U\n  %a\n  %i" :empty-lines 1)

          ("j" "Journal Entries")
          ("jj" "Journal" entry
           (file+olp+datetree swarsel-org-journal-filepath)
           "\n* %<%I:%M %p> - Journal :journal:\n\n%?\n\n"
           ;; ,(dw/read-file-as-string "~/Notes/Templates/Daily.org")
           :clock-in :clock-resume
           :empty-lines 1)))

  (swarsel/org-font-setup))

(defun swarsel/org-font-setup ()
  ;; Replace list hyphen with dot
  (font-lock-add-keywords 'org-mode
                          '(("^ *\\([-]\\) "
                             (0 (prog1 () (compose-region (match-beginning 1) (match-end 1) "•")))))))


;; Set faces for heading levels
(with-eval-after-load 'org-faces  (dolist (face '((org-level-1 . 1.2)
                                                  (org-level-2 . 1.1)
                                                  (org-level-3 . 1.05)
                                                  (org-level-4 . 1.0)
                                                  (org-level-5 . 1.1)
                                                  (org-level-6 . 1.1)
                                                  (org-level-7 . 1.1)
                                                  (org-level-8 . 1.1)))
                                    (set-face-attribute (car face) nil :font swarsel-alt-font :weight 'regular :height (cdr face)))

                      ;; Ensure that anything that should be fixed-pitch in Org files appears that way
                      (set-face-attribute 'org-block nil :foreground nil :inherit '(fixed-pitch))
                      (set-face-attribute 'org-code nil   :inherit '(shadow fixed-pitch))
                      (set-face-attribute 'org-table nil   :inherit '(shadow fixed-pitch))
                      (set-face-attribute 'org-verbatim nil :inherit '(shadow fixed-pitch))
                      (set-face-attribute 'org-special-keyword nil :inherit '(font-lock-comment-face fixed-pitch))
                      (set-face-attribute 'org-meta-line nil :inherit '(font-lock-comment-face fixed-pitch))
                      (set-face-attribute 'org-checkbox nil :inherit '(fixed-pitch)))

(use-package org-bullets
  :after org
  :hook (org-mode . org-bullets-mode)
  :custom
  (org-bullets-bullet-list '("◉" "○" "●" "○" "●" "○" "●")))

(defun swarsel/org-mode-visual-fill ()
  (setq visual-fill-column-width 100
        visual-fill-column-center-text t)
  (visual-fill-column-mode 1))

(use-package visual-fill-column
  :hook (org-mode . swarsel/org-mode-visual-fill))

(org-babel-do-load-languages
  'org-babel-load-languages
  '((emacs-lisp . t)
    (python . t)))

(push '("conf-unix" . conf-unix) org-src-lang-modes)

(require 'org-tempo)
(add-to-list 'org-structure-template-alist '("sh" . "src shell"))
(add-to-list 'org-structure-template-alist '("el" . "src emacs-lisp"))
(add-to-list 'org-structure-template-alist '("py" . "src python"))

(defun swarsel/org-babel-tangle-config ()
  (when (string-equal (buffer-file-name)
                      swarsel-emacs-org-filepath)
    ;; Dynamic scoping to the rescue
    (let ((org-confirm-babel-evaluate nil))
      (org-babel-tangle))))

(add-hook 'org-mode-hook (lambda () (add-hook 'after-save-hook #'swarsel/org-babel-tangle-config)))

;(use-package tex
  ;  :ensure auctex)

(add-hook 'markdown-mode-hook
   (lambda ()
     (local-set-key (kbd "C-c C-x C-l") 'org-latex-preview)
     (local-set-key (kbd "C-c C-x C-u") 'markdown-toggle-url-hiding)
     ))

(use-package org-download
  :after org
  :defer nil
  :custom
  (org-download-method 'directory)
  (org-download-image-dir "./images")
  (org-download-heading-lvl 0)
  (org-download-timestamp "org_%Y%m%d-%H%M%S_")
  ;;(org-image-actual-width 500)
  (org-download-screenshot-method "grim -g \"$(slurp)\" %s")
  :bind
  ("C-M-y" . org-download-screenshot)
  :config
  (require 'org-download))

(use-package org-fragtog)
(add-hook 'org-mode-hook 'org-fragtog-mode)
(add-hook 'markdown-mode-hook 'org-fragtog-mode)

;; https://github.com/mooreryan/markdown-dnd-images
          (add-to-list 'load-path "~/.emacs.d/packages")
           (require 'markdown-dnd-images)
             (setq dnd-save-directory "images")

              (setq dnd-save-buffer-name nil)

              (setq dnd-view-inline t)

              (setq dnd-capture-source nil)

;; these next lines provide an interface for org-download in markdown mode for use with obsidian

      (defvar org-download-markdown-link-format
        "![[./%s]]\n"
        "Format of the file link to insert.")

      (defcustom org-download-markdown-link-format-function #'org-download-markdown-link-format-function-default
      "Function that takes FILENAME and returns a org link."
      :type 'function)

    (defun org-download-markdown-link-format-function-default (filename)
      "The default function of `org-download-link-format-function'."
      (if (and (>= (string-to-number org-version) 9.3)
               (eq org-download-method 'attach))
          (format "[[attachment:%s]]\n"
                  (org-link-escape
                   (file-relative-name filename (org-attach-dir))))
        (format org-download-markdown-link-format
                (org-link-escape
                 (funcall org-download-abbreviate-filename-function filename)))))

    (defun org-download-markdown-image (link)
    "Save image at address LINK to `org-download--dir'."
    (interactive "sUrl: ")
    (let* ((link-and-ext (org-download--parse-link link))
           (filename
            (cond ((and (derived-mode-p 'org-mode)
                        (eq org-download-method 'attach))
                   (let ((org-download-image-dir (org-attach-dir t))
                         org-download-heading-lvl)
                     (apply #'org-download--fullname link-and-ext)))
                  ((fboundp org-download-method)
                   (funcall org-download-method link))
                  (t
                   (apply #'org-download--fullname link-and-ext)))))
      (setq org-download-path-last-file filename)
      (org-download--image link filename)
      (when (org-download-org-mode-p)
        (when (eq org-download-method 'attach)
          (org-attach-attach filename nil 'none))
        (org-download-markdown-insert-link link filename))
      (when (and (eq org-download-delete-image-after-download t)
                 (not (url-handler-file-remote-p (current-kill 0))))
        (delete-file link delete-by-moving-to-trash))))

  (defun org-download-markdown-screenshot (&optional basename)
    "Capture screenshot and insert the resulting file.
  The screenshot tool is determined by `org-download-screenshot-method'."
    (interactive)
    (let* ((screenshot-dir (file-name-directory org-download-screenshot-file))
           (org-download-screenshot-file
            (if basename
                (concat screenshot-dir basename) org-download-screenshot-file)))
      (make-directory screenshot-dir t)
      (if (functionp org-download-screenshot-method)
          (funcall org-download-screenshot-method
                   org-download-screenshot-file)
        (shell-command-to-string
         (format org-download-screenshot-method
                 org-download-screenshot-file)))
      (when (file-exists-p org-download-screenshot-file)
        (org-download-markdown-image org-download-screenshot-file)
        (delete-file org-download-screenshot-file))))


      (defun org-download-markdown-insert-link (link filename)
      (let* ((beg (point))
             (line-beg (line-beginning-position))
             (indent (- beg line-beg))
             (in-item-p (org-in-item-p))
             str)
        (if (looking-back "^[ \t]+" line-beg)
            (delete-region (match-beginning 0) (match-end 0))
          (newline))
        (insert (funcall org-download-annotate-function link))
        (dolist (attr org-download-image-attr-list)
          (insert attr "\n"))
        (insert (if (= org-download-image-html-width 0)
                    ""
                  (format "#+attr_html: :width %dpx\n" org-download-image-html-width)))
        (insert (if (= org-download-image-latex-width 0)
                    ""
                  (format "#+attr_latex: :width %dcm\n" org-download-image-latex-width)))
        (insert (if (= org-download-image-org-width 0)
                    ""
                  (format "#+attr_org: :width %dpx\n" org-download-image-org-width)))
        (insert (funcall org-download-markdown-link-format-function filename))
        (org-download--display-inline-images)
        (setq str (buffer-substring-no-properties line-beg (point)))
        (when in-item-p
          (indent-region line-beg (point) indent))
        str))

          (defun markdown-download-screenshot ()
            (interactive)
            (org-mode)
            (org-download-markdown-screenshot)
            (markdown-mode))

(add-hook 'markdown-mode-hook (lambda () (org-display-inline-images)))

(use-package rg)

(use-package projectile
  :diminish projectile-mode
  :config (projectile-mode)
  :custom ((projectile-completion-system 'ivy)) ;; integrate ivy into completion system
  :bind-keymap
  ("C-c p" . projectile-command-map) ; all projectile commands under this
  :init
  ;; NOTE: Set this to the folder where you keep your Git repos!
  (when (file-directory-p swarsel-projects-directory)
    (setq projectile-project-search-path (list swarsel-projects-directory)))
  (setq projectile-switch-project-action #'projectile-dired)) ;list files

(use-package counsel-projectile
  :config (counsel-projectile-mode))

(use-package magit
  :config
  (setq magit-repository-directories `((,swarsel-projects-directory  . 1)
                                      (,swarsel-emacs-directory . 0)
                                      (,swarsel-obsidian-directory . 0)))
  :custom
  (magit-display-buffer-function #'magit-display-buffer-same-window-except-diff-v1)) ; stay in the same window

;; NOTE: Make sure to configure a GitHub token before using this package!
;; - https://magit.vc/manual/forge/Token-Creation.html#Token-Creation
;; - https://magit.vc/manual/ghub/Getting-Started.html#Getting-Started
;; - https://magit.vc/manual/ghub/Storing-a-Token.html
;; - https://www.emacswiki.org/emacs/GnuPG

;; (1) in practice: github -<> settings -<> developer option -<>
;;       create classic token with repo; user; read:org permissions
;; (2) install GnuGP (and add to PATH)
;; (3) create ~/.authinfo.gpg with the following info scheme:
;;       machine api.github.com login USERNAME^forge password 012345abcdef...
  (use-package forge)

(use-package rainbow-delimiters
  :hook (prog-mode . rainbow-delimiters-mode))

(use-package paren
  :config
   (set-face-background 'show-paren-match "dark violet")
   (set-face-foreground 'show-paren-match "gold")
   (set-face-attribute 'show-paren-match nil :weight 'extra-bold))


   (use-package highlight-parentheses)
     (define-globalized-minor-mode global-highlight-parentheses-mode
       highlight-parentheses-mode
       (lambda ()
         (highlight-parentheses-mode t)))
     (global-highlight-parentheses-mode t)

(defun swarsel/lsp-mode-setup ()
 (setq lsp-headerline-breadcrumb-segments '(path-up-to-project file symbols))
 (lsp-headerline-breadcrumb-mode))

(use-package lsp-mode
  :commands (lsp lsp-deferred)
  :hook (lsp-mode . swarsel/lsp-mode-setup)
  :init
  (setq lsp-keymap-prefix "C-c l")  ;; Or 'C-l', 's-l'
  :config
  (lsp-enable-which-key-integration t))

(use-package company
  :after lsp-mode
  :hook (lsp-mode . company-mode)
 ; :bind (:map company-active-map
 ;      ("<tab>" . company-complete-selection))
 ;     (:map lsp-mode-map
 ;      ("<tab>" . company-indent-or-complete-common))
  :custom
  (company-minimum-prefix-length 1)
  (company-idle-delay 0.0))

(use-package company-box
  :hook (company-mode . company-box-mode))

(use-package lsp-ui
:hook (lsp-mode . lsp-ui-mode)
:config
(define-key lsp-ui-mode-map [remap xref-find-definitions] #'lsp-ui-peek-find-definitions)
(define-key lsp-ui-mode-map [remap xref-find-references] #'lsp-ui-peek-find-references)
(setq lsp-ui-doc-enable t
      lsp-ui-doc-show-with-cursor t
      lsp-ui-doc-include-signature t
      lsp-ui-sideline.enable t
      lsp-ui-sideline-show-diagnostics t
      lsp-ui-sideline-show-hover t
      lsp-ui-sideline-show-code-actions t
      lsp-ui-sideline-ignore-duplicate t
      lsp-ui-doc-position 'top)
      lsp-ui-imenu-enable t)

(use-package lsp-treemacs
:after lsp)

(use-package lsp-ivy)

(use-package dap-mode)
(require 'dap-python)
(dap-mode 1)
(setq dap-auto-configure-mode nil)
    ;; The modes below are optional
    (dap-ui-mode 1)
    ;; enables mouse hover support
    (dap-tooltip-mode 1)
    ;; use tooltips for mouse hover
    ;; if it is not enabled `dap-mode' will use the minibuffer.
    ;; (tooltip-mode 1)
    ;; displays floating panel with debug buttons
    ;; requies emacs 26+;; displays floating panel with debug buttons
    ;; requies emacs 26+
    (dap-ui-controls-mode 0)
    (setq dap-python-debugger 'debugpy)

(use-package typescript-mode
  :mode "\\.ts\\'"
  :hook (typescript-mode . lsp-deferred)
  :config
  (setq typescript-indent-level 2))

(use-package python-mode
  :ensure t
  :hook (python-mode . lsp-deferred)
  ;;:custom
  ;; NOTE: Set this if Python 3 is called "python3"
  ;; (python-shell-interpreter "python3")
  ;;(dap-python-executable "python3")
  )

(use-package evil-nerd-commenter
:bind ("M-/" . evilnc-comment-or-uncomment-lines))

(setq gac-automatically-push-p t
      gac-automatically-add-new-files-p t)

(use-package yasnippet)

(defun duplicate-line (arg)
    "Duplicate current line, leaving point in lower line."
    (interactive "*p")

    ;; save the point for undo
    (setq buffer-undo-list (cons (point) buffer-undo-list))

    ;; local variables for start and end of line
    (let ((bol (save-excursion (beginning-of-line) (point)))
          eol)
      (save-excursion

        ;; don't use forward-line for this, because you would have
        ;; to check whether you are at the end of the buffer
        (end-of-line)
        (setq eol (point))

        ;; store the line and disable the recording of undo information
        (let ((line (buffer-substring bol eol))
              (buffer-undo-list t)
              (count arg))
          ;; insert the line arg times
          (while (> count 0)
            (newline)         ;; because there is no newline in 'line'
            (insert line)
            (setq count (1- count)))
          )

        ;; create the undo information
        (setq buffer-undo-list (cons (cons eol (point)) buffer-undo-list)))
      ) ; end-of-let

    ;; put the point in the lowest line and return
    (next-line arg))

(global-set-key (kbd "C-C d") 'duplicate-line)

(setq backup-by-copying-when-linked t)

(use-package dired
    :ensure nil
    :commands (dired dired-jump)
    :bind (("C-x C-j" . dired-jump))
    :custom ((dired-listing-switches "-agho --group-directories-first"))
    :config
    (evil-collection-define-key 'normal 'dired-mode-map
      "h" 'dired-single-up-directory
      "l" 'dired-single-buffer))

  (use-package dired-single)

  (use-package all-the-icons-dired
    :hook (dired-mode . all-the-icons-dired-mode))

(use-package dired-toggle-sudo)
(define-key dired-mode-map (kbd "C-c C-s") 'dired-toggle-sudo)
  ;; (use-package dired-open
  ;;   :config
  ;;   ;; Doesn't work as expected!
  ;;   ;;(add-to-list 'dired-open-functions #'dired-open-xdg t)
  ;;   (setq dired-open-extensions '(("png" . "feh")
  ;;                                 ("mkv" . "mpv"))))

(use-package obsidian
  :ensure t
  :demand t
  :config
  (obsidian-specify-path swarsel-obsidian-vault-directory)
  (global-obsidian-mode t)
  :custom
  ;; This directory will be used for `obsidian-capture' if set.
  (obsidian-inbox-directory "Inbox")
  (bind-key (kbd "C-c M-o") 'obsidian-hydra/body 'obsidian-mode-map)
  :bind (:map obsidian-mode-map
              ;; Replace C-c C-o with Obsidian.el's implementation. It's ok to use another key binding.
              ("C-c C-o" . obsidian-follow-link-at-point)
              ;; Jump to backlinks
              ("C-c C-b" . obsidian-backlink-jump)
              ;; If you prefer you can use `obsidian-insert-link'
              ("C-c C-l" . obsidian-insert-wikilink)))

(use-package anki-editor
  :after org
  :bind (:map org-mode-map
              ("<f12>" . anki-editor-cloze-region-auto-incr)
              ("<f11>" . anki-editor-cloze-region-dont-incr)
              ("<f10>" . anki-editor-reset-cloze-number)
              ("<f9>"  . anki-editor-push-tree))
  :hook (org-capture-after-finalize . anki-editor-reset-cloze-number) ; Reset cloze-number after each capture.
  :config
  (setq anki-editor-create-decks t ;; Allow anki-editor to create a new deck if it doesn't exist
        anki-editor-org-tags-as-anki-tags t)

  (defun anki-editor-cloze-region-auto-incr (&optional arg)
    "Cloze region without hint and increase card number."
    (interactive)
    (anki-editor-cloze-region swarsel-anki-editor-cloze-number "")
    (setq swarsel-anki-editor-cloze-number (1+ swarsel-anki-editor-cloze-number))
    (forward-sexp))
  (defun anki-editor-cloze-region-dont-incr (&optional arg)
    "Cloze region without hint using the previous card number."
    (interactive)
    (anki-editor-cloze-region (1- swarsel-anki-editor-cloze-number) "")
    (forward-sexp))
  (defun anki-editor-reset-cloze-number (&optional arg)
    "Reset cloze number to ARG or 1"
    (interactive)
    (setq swarsel-anki-editor-cloze-number (or arg 1)))
  (defun anki-editor-push-tree ()
    "Push all notes under a tree."
    (interactive)
    (anki-editor-push-notes '(4))
    (anki-editor-reset-cloze-number))
  ;; Initialize
  (anki-editor-reset-cloze-number)
  )

(require 'anki-editor)

(defvar swarsel-anki-deck nil)
(defvar swarsel-anki-notetype nil)
(defvar swarsel-anki-fields nil)

(defun swarsel-anki-set-deck-and-notetype ()
  (interactive)
         (setq swarsel-anki-deck  (completing-read "Choose a deck: "
                                      (sort (anki-editor-deck-names) #'string-lessp)))
         (setq swarsel-anki-notetype (completing-read "Choose a note type: "
                                    (sort (anki-editor-note-types) #'string-lessp)))
         (setq swarsel-anki-fields (progn
         (anki-editor--anki-connect-invoke-result "modelFieldNames" `((modelName . ,swarsel-anki-notetype)))))
        )

(defun swarsel-anki-make-template-string ()
  (if (not swarsel-anki-deck)
      (call-interactively 'swarsel-anki-set-deck-and-notetype))
  (setq swarsel-temp swarsel-anki-fields)
  (concat (concat "* %<%H:%M>\n:PROPERTIES:\n:ANKI_NOTE_TYPE: " swarsel-anki-notetype "\n:ANKI_DECK: " swarsel-anki-deck "\n:END:\n** ")(pop swarsel-temp) "\n%?\n** " (mapconcat 'identity swarsel-temp "\n\n** ") "\n\n"))

(defun swarsel-today()
  (format-time-string "%Y-%m-%d"))

(defun swarsel-obsidian-daily ()
  (interactive)
  (if (not (file-exists-p (expand-file-name (concat (swarsel-today) ".md") swarsel-obsidian-daily-directory)))
      (write-region "" nil (expand-file-name (concat (swarsel-today) ".md") swarsel-obsidian-daily-directory))
    )
  (find-file (expand-file-name (concat (swarsel-today) ".md") swarsel-obsidian-daily-directory)))

(defun swarsel-magit-fetch-certain-repositories()
    (setq default-directory swarsel-obsidian-directory)
    (magit-fetch-all (magit-fetch-arguments))
    (magit-pull-from-pushremote (magit-pull-arguments)))
    ;; (setq default-directory swarsel-emacs-directory)
    ;; (magit-fetch-all (magit-fetch-arguments))
    ;; (magit-pull-from-pushremote (magit-pull-arguments)))

(add-hook 'emacs-startup-hook 'swarsel-magit-fetch-certain-repositories)

(server-start)

;; Make gc pauses faster by decreasing the threshold.
(setq gc-cons-threshold (* 2 1000 1000))
