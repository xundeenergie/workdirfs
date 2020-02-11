# workdirfs

This repo contains a fuse-filesystem, which creates automagically a directory in users $HOME 
and subdir in directory $HOME/archive/workdir with todays date as subdirname. 
All directories are created, if not existent.

It also contains a systemd-unit for users systemd-process, which will start on login and ends, when user logs out.

Run setup.sh, to install it for one user.

Run setup-system.sh to install it for all users

## System Requriements

### Debian based systems
```
    sudo apt install python3-fuse python3-fusepy
```

### Redhat based systems
```
    sudo dnf install python3-fusepy
```
