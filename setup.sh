#!/bin/sh

FUSERMOUNT=$(which fusermount)
echo $FUSERMOUNT
. ./uninstall.sh

echo "Install workdirfs for all users"
sudo cp workdirfs.py /usr/local/bin/workdirfs.py
sudo cp workdirfs.service /etc/systemd/user/workdirfs.service
echo replace 
sudo sed -i -e "s@%FUSERMOUNT%@${FUSERMOUNT}@" /etc/systemd/user/workdirfs.service
echo replaced
sudo mkdir -pv /etc/systemd/user/default.target.wants/
sudo ln -sf ../workdirfs.service /etc/systemd/user/default.target.wants/workdirfs.service
systemctl --user daemon-reload
systemctl --user restart workdirfs.service
