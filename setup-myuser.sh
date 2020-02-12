#!/bin/sh

sudo cp workdirfs.py /usr/local/bin/workdirfs.py
cp workdirfs.service ~/.config/systemd/user/workdirfs.service
sudo mkdir -pv ~/.config/systemd/user/default.target.wants/
sudo ln -sf ../workdirfs.service ~/.config/systemd/user/default.target.wants/workdirfs.service
cp workdirfs.config ~/.config/workdirfs.conf
sudo cp workdirfs.config /etc/workdirfs.conf
systemctl --user daemon-reload
systemctl --user restart workdirfs.service
