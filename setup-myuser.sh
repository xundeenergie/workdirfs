#!/bin/sh

sudo cp workdirfs.py /usr/local/bin/workdirfs.py
cp workdirfs.service ~/.config/systemd/user/workdirfs.service
mkdir -pv ~/.config/systemd/user/default.target.wants/
ln -sf ../workdirfs.service ~/.config/systemd/user/default.target.wants/workdirfs.service
systemctl --user daemon-reload
systemctl --user restart workdirfs.service
