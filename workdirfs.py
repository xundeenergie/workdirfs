#!/usr/bin/env -S  python3 -u

from __future__ import with_statement

import os
import sys
import errno

from datetime import datetime, timedelta
import time

import fileinput

import argparse

try:
    from fuse import FUSE, FuseOSError, Operations
except:
    try:
        from fusepy import FUSE, FuseOSError, Operations
    except:
        print("please install fusepy")
        raise errno.ENOENT


class WorkdirFS(Operations):
    def __init__(self, args):
        self.args = args

    # Helpers
    # =======

    def _full_path(self, partial):
        today = datetime.now() - timedelta(hours=self.args.timeoffset)
        if self.args.yearlydir:
            path = os.path.join(self.args.archive,"workdir",today.strftime("%Y"))
            if self.args.monthlydir:
                path = os.path.join(path, today.strftime("%m"))
        else:
            path = os.path.join(self.args.archive, "workdir")

        if partial.startswith("/"):
            partial = partial[1:]

        path = os.path.join(check_dir(os.path.join(path, today.strftime("%Y-%m-%d"))), partial)

        return path

    # Filesystem methods
    # ==================

    def access(self, path, mode):
        full_path = self._full_path(path)
        if not os.access(full_path, mode):
            raise FuseOSError(errno.EACCES)

    def chmod(self, path, mode):
        full_path = self._full_path(path)
        return os.chmod(full_path, mode)

    def chown(self, path, uid, gid):
        full_path = self._full_path(path)
        return os.chown(full_path, uid, gid)

    def getattr(self, path, fh=None):
        full_path = self._full_path(path)
        st = os.lstat(full_path)
        return dict((key, getattr(st, key)) for key in ('st_atime',
                                                        'st_ctime',
                                                        'st_gid',
                                                        'st_mode',
                                                        'st_mtime',
                                                        'st_nlink',
                                                        'st_size',
                                                        'st_uid'))

    def readdir(self, path, fh):
        full_path = self._full_path(path)

        dirents = ['.', '..']
        if os.path.isdir(full_path):
            dirents.extend(os.listdir(full_path))
        for r in dirents:
            yield r

    def readlink(self, path):
        pathname = os.readlink(self._full_path(path))
        if pathname.startswith("/"):
            # Path name is absolute, sanitize it.
            return os.path.relpath(pathname, self.args.archive)
        else:
            return pathname

    def mknod(self, path, mode, dev):
        return os.mknod(self._full_path(path), mode, dev)

    def rmdir(self, path):
        full_path = self._full_path(path)
        return os.rmdir(full_path)

    def mkdir(self, path, mode):
        return os.mkdir(self._full_path(path), mode)

    def statfs(self, path):
        full_path = self._full_path(path)
        stv = os.statvfs(full_path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail',
                                                         'f_bfree',
                                                         'f_blocks',
                                                         'f_bsize',
                                                         'f_favail',
                                                         'f_ffree',
                                                         'f_files',
                                                         'f_flag',
                                                         'f_frsize',
                                                         'f_namemax'))

    def unlink(self, path):
        return os.unlink(self._full_path(path))

    def symlink(self, name, target):
        return os.symlink(target, self._full_path(name))

    def rename(self, old, new):
        return os.rename(self._full_path(old), self._full_path(new))

    def link(self, target, name):
        return os.link(self._full_path(name), self._full_path(target))

    def utimens(self, path, times=None):
        return os.utime(self._full_path(path), times)

    # File methods
    # ============

    def open(self, path, flags):
        full_path = self._full_path(path)
        return os.open(full_path, flags)

    def create(self, path, mode, fi=None):
        full_path = self._full_path(path)
        return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

    def read(self, path, length, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.read(fh, length)

    def write(self, path, buf, offset, fh):
        os.lseek(fh, offset, os.SEEK_SET)
        return os.write(fh, buf)

    def truncate(self, path, length, fh=None):
        full_path = self._full_path(path)
        with open(full_path, 'r+') as f:
            f.truncate(length)

    def flush(self, path, fh):
        return os.fsync(fh)

    def release(self, path, fh):
        return os.close(fh)

    def fsync(self, path, fdatasync, fh):
        return self.flush(path, fh)

def cleanup_dirs(root):

    today = datetime.now() - timedelta(hours=2)
    today = today.strftime("%Y-%m-%d")

    for root, dirs, files in os.walk(root, topdown=False):
        for _dir in dirs:
            print("cleanup",os.path.join(root, _dir))
            if not _dir == today and not os.listdir(os.path.join(root, _dir)):
                print("""Directory is empty -> remove it (not now implemented for
                        testpurpose)""",
                      os.path.join(root, _dir))


def check_dir(path):
    checkdir = os.path.isdir(path)
    if not checkdir:
        try:
            os.makedirs(path, exist_ok=True)
            print("Created directory {}".format(path), flush=True)
        except:
            print("[-] Makedir error")
    return path

def main(args):
    #FUSE(WorkdirFS(root), mountpoint, nothreads=True, foreground=True)
    check_dir(args.archive)
    check_dir(args.mountpoint)
    cleanup_dirs(args.archive)
    # first search if configuration exists for xdg-userdirs
    # to use it with alias gowork and goarchive
    foundarchive=False
    foundwork=False
    with fileinput.input(os.environ['HOME']+'/.config/user-dirs.dirs',
            inplace=True) as fh:
        for line in fh:
            if line.startswith('XDG_ARCHIVE_DIR'):
                print("XDG_ARCHIVE_DIR=\""+args.archive+'"\n')
                foundarchive=True
            elif line.startswith('XDG_WORK_DIR'):
                print("XDG_WORK_DIR=\""+args.mountpoint+'"\n')
                foundwork=True
            else:
                 print(line, end='')
    if not foundarchive:
        with open(os.environ['HOME']+'/.config/user-dirs.dirs', 'a') as fh:
            fh.write("XDG_ARCHIVE_DIR=\""+args.archive+'"\n')
    if not foundwork:
        with open(os.environ['HOME']+'/.config/user-dirs.dirs', 'a') as fh:
            fh.write("XDG_WORK_DIR=\""+args.mountpoint+'"\n')

    # start FUSE filesystem
    FUSE(WorkdirFS(args), args.mountpoint, nothreads=True, foreground=True)

if __name__ == '__main__':
    #main(sys.argv[2], sys.argv[1])
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--archive",
            default=os.environ['HOME']+'/archive', help="Path to archivedir-base")
    parser.add_argument("-m", "--mountpoint",
            default=os.environ['HOME']+'/Work', help='Path to Workdir')
    parser.add_argument("-t", "--timeoffset", type=int, default=2, help="""If you're working
            all day till 3 o'clock in the morning, set it to 4, so next day
            archive-dir will be created 4 hours after midnight. You have 1h
            tolerance, if you're working one day a little bit longer""")
    parser.add_argument("-y", "--yearlydir", action="store_true")
    parser.add_argument("-M", "--monthlydir", action="store_true")
    args = parser.parse_args()
    print(args)
    #root = os.environ['HOME']+'/archive'
    #mountpoint = os.environ['HOME']+'/Work'
    main(args)
