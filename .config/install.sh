#!/bin/bash 

sudo dnf install firefox
sudo dnf install sway
sudo dnf install wofi
sudo dnf install kitten
sudo dnf install zsh
sudo dnf install waybar
sudo dnf install git
sudo dnf install gh


sudo timedatectl set-ntp yes
sudo timedatectl set-local-rtc 0



cd ~
echo ".cfg" >> .gitignore
git clone https://github.com/Swarsel/dotfiles $HOME/.cfg
alias config='/usr/bin/git --git-dir=$HOME/.cfg/ --work-tree=$HOME'
config config --local status.showUntrackedFiles no
config checkout
