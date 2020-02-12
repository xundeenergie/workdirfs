#!/bin/bash

echo "Remove workdirfs"
echo "stop workdirfs.service"
systemctl --user stop workdirfs.service
echo "remove binaries and units from system"
sudo rm -rf /usr/local/bin/workdirfs.py /etc/systemd/user/workdirfs.service /etc/systemd/user/default.target.wants/workdirfs
echo "remove systemd-units for this user $USER"
rm -rf ~/.config/systemd/user/workdirfs.service ~/.config/systemd/user/default.target.wants/workdirfs.service
