#!/bin/bash
/usr/bin/git --git-dir=$HOME/.cfg/ --work-tree=$HOME commit -a -m "Automatic EOS commit"
/usr/bin/git --git-dir=$HOME/.cfg/ --work-tree=$HOME push
