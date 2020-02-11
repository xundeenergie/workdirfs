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
And then reload users systemd
```
    systemctl --user daemon-reload
    systemctl --user restart workdirfs.service
```


