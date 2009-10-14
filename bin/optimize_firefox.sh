#!/bin/bash

killall firefox-bin
find $HOME/.mozilla/ \( -name "*.sqlite" \) -exec sqlite3  {} "vacuum" \;

