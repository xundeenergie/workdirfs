# workdirfs

This repo contains a fuse-filesystem, which creates automagically a directory in users $HOME 
and subdir in directory $HOME/archive/workdir with todays date as subdirname. 
All directories are created, if not existent.

It also contains a systemd-unit for users systemd-process, which will start on login and ends, when user logs out.

## System Requriements

python3 is requried and also this packages:

### Debian based systems
```
    sudo apt install python3-fuse python3-fusepy
```

### Redhat based systems
```
    sudo dnf install python3-fusepy
```


## Installation

Run setup.sh, to install it for all user.
This script will do the next steps for you. Reload users systemd and start service
And then reload users systemd
```
    systemctl --user daemon-reload
    systemctl --user restart workdirfs.service
```

### Alias
If you want, add an alias in your configuration (e.g. ~/.bashrc /etc/bash.bashrc /etc/profile.d/aliases... whatever you want) to go quick to archive or ~/Work.

```
    alias gowork='[ -e $(xdg-user-dir WORK) ] && cd $(xdg-user-dir WORK)'
    alias goarchive='[ -e $(xdg-user-dir ARCHIVE) ] && cd $(xdg-user-dir ARCHIVE)'
```
On every restart of users systemd, the xdg-configuration for xdg-user-dir WORK and ARCHIVE is being updated, so the alias should work always. Even if you change the path to XDG\_WORK\_DIR or XDG\_ARCHIVE\_DIR in systemd unit.
