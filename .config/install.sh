#!/bin/bash 
su

sudo dnf install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm -y
sudo dnf update
sudo dnf install firefox emacs sway wofi kitten zsh waybar git gh network-manager-applet blueman discord mako flatpak lpf-spotify-client xournalpp wl-clipboard -y

lpf update

flatpak install flathub chat.schildi.desktop --hidden   

sudo timedatectl set-ntp yes
sudo timedatectl set-local-rtc 0

pip install python-lsp-server
pip install debugpy

cd ~
echo ".cfg" >> .gitignore
git clone https://github.com/Swarsel/dotfiles $HOME/.cfg
alias config='/usr/bin/git --git-dir=$HOME/.cfg/ --work-tree=$HOME'
config config --local status.showUntrackedFiles no
config checkout
