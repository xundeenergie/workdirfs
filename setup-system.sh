#!/bin/sh

sudo cp workdirfs.py /usr/local/bin/workdirfs.py
sudo cp workdirfs.service /etc/systemd/user/workdirfs.service
sudo mkdir -pv /etc/systemd/user/default.target.wants/workdirfs.service
sudo ln -sf ../workdirfs.service /etc/systemd/user/default.target.wants/workdirfs.service
systemctl --user daemon-reload
systemctl --user restart workdirfs.service
