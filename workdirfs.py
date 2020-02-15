#!/usr/bin/env -S  python3 -u

from __future__ import with_statement

import os
import sys
import errno

from datetime import datetime, timedelta, date
import time

import fileinput

import argparse
import gzip
import shutil
import json
import traceback

try:
    from fuse import FUSE, FuseOSError, Operations
except:
    try:
        from fusepy import FUSE, FuseOSError, Operations
    except:
        print("please install fusepy")
        raise errno.ModuleNotFoundError


class WorkdirFS(Operations):
    def __init__(self, args):
        self.args = args

        # init configdir and configlast
        self.confdir = os.path.join(os.environ['HOME'], '.local', 'workdirfs')
        self.configlast = os.path.join(self.confdir, 'yesterday')

        self._checkdir(self.confdir)

        # init archivbase and xdg_archive
        if self.args.archive.startswith("/"):
            self.archivpathbase = self.args.archive
            self.xdgarchivpathbase = self.args.archive
        else:
            self.archivpathbase = os.path.join(os.environ['HOME'], self.args.archive)
            self.xdgarchivpathbase = os.path.join('"$HOME', self.args.archive)

        self._xdg()
        self._give_me_today()
        self.todaypath = self._checkdir(self._give_me_archivpath())
        self.yesterdaypath = self._checkdir(self._give_me_archivpath(self._give_me_yesterday()))

        print("initial yesterdaypath is {}".format(self.yesterdaypath))
        print("initial todaypath is {}".format(self.todaypath))

    # Helpers
    # =======

    def _xdg(self):
        foundarchive=False
        foundwork=False
        xdguserdirs = os.environ['HOME']+'/.config/user-dirs.dirs'
        try:
            with fileinput.input(xdguserdirs, inplace=True) as fh:
                for line in fh:
                    if line.startswith('XDG_ARCHIVE_DIR'):
                        print("XDG_ARCHIVE_DIR=" + self.xdgarchivpathbase, end='\n')
                        foundarchive=True
                    elif line.startswith('XDG_WORK_DIR'):
                        print("XDG_WORK_DIR=\"$HOME/" + self.args.mountpoint +'"', end='\n')
                        foundwork=True
                    else:
                         print(line, end='')
        except:
            print("File not existing, create it: {}".format(xdguserdirs))

        if not foundarchive:
            with open(xdguserdirs, 'a') as fh:
                fh.write("XDG_ARCHIVE_DIR=" + self.xdgarchivpathbase + '\n')
        if not foundwork:
            with open(xdguserdirs, 'a') as fh:
                fh.write('XDG_WORK_DIR=\"$HOME/' + self.args.mountpoint + '"\n')

    def _give_me_today(self):
        self.today = datetime.now() - timedelta(hours=self.args.timeoffset)
        return self.today

    def _give_me_yesterday(self):
        if os.path.exists(self.configlast):
            with open(self.configlast, 'r') as fh:
                self.yesterday = datetime.strptime(fh.readline().strip(), "%Y-%m-%d")
        else:
            self.yesterday = self.today
            self._checkdir(self.confdir)
            if not os.path.isdir(self.confdir):
                os.mkdir(self.confdir)
            with open(self.configlast, 'w') as fh:
                fh.write(self.yesterday.date().strftime("%Y-%m-%d"))
        return self.yesterday

    def _give_me_archivpath(self, _date=None):
        archivpathbase = self.archivpathbase
        if _date == None:
            _date = self.today
        if self.args.yearlydir:
            archivpathbase = os.path.join(archivpathbase, _date.strftime("%Y"))
        if self.args.monthlydir:
            archivpathbase = os.path.join(archivpathbase, _date.strftime("%m"))
        if self.args.weeklydir:
            archivpathbase = os.path.join(archivpathbase, int(_date.strftime("%W"))+1)
        self.archivpath = os.path.join(archivpathbase, _date.strftime("%Y-%m-%d"))
        return self.archivpath

    def _checkdir(self, path):
        if not os.path.exists(path) and not os.path.isdir(path):
            try:
                os.makedirs(path, exist_ok=True)
                print("Created directory {}".format(path), flush=True)
            except Exception as e:
                print("[-] Error while check dir and zip files: ", e)

#        if yesterdaypath != None and todaypath != None:
#            print("yesterdaypath: {}, todaypath: {}".format(yesterdaypath, todaypath))
#            if todaypath != yesterdaypath:
#                _zipfiles(yesterdaypath)
#                #Create .yesterdaypath in archive with yesterdaypath inside
#                wdconfigdir = os.path.join(os.environ['HOME'], '.local', 'workdirfs')
#                print("New yesterdaypath is {}".format(todaypath))
#                with open(os.path.join(wdconfigdir, 'yesterdaypath'), 'w+') as f:
#                    f.write(todaypath)

        return path


    def _full_path(self, partial):

        #self._give_me_today()
        path = self._give_me_archivpath()
        self._give_me_yesterday()

        if partial.startswith("/"):
            partial = partial[1:]


        path = os.path.join(
                self._checkdir( self._give_me_archivpath(self._give_me_today())),
                partial
            )

        if self.today.date() > self.yesterday.date():
            self._cleanup_dirs()
            print("zip yesterday: ", self.yesterdaypath)
            self.yesterday = self.today
            self.yesterdaypath = self.todaypath

        with open(self.configlast, 'w') as fh:
            fh.write(self.today.strftime("%Y-%m-%d"))

#        print("yesterdaypath: {}, todaypath: {}".format(self.yesterdaypath, self.todaypath))
#        print("yesterday: {}, today: {}".format(self.yesterday.date(), self.today.date()))
        return path


    def _cleanup_dirs(self):

        print("Cleanup dir", self.yesterdaypath)
        zip_fileext=".gz"
        zip_compressionlevel=5
        for root, dirs, files in os.walk(self.yesterdaypath, topdown=False):
            for d in dirs:
                print("cleanup",os.path.join(root, d))
                if not _dir == self.todaypath and not os.listdir(os.path.join(root, d)):
                    print("Directory is empty -> remove it",
                          os.path.join(root, d))
                    os.remove(os.path.join(root, d))
            for f in files:
                print("compress", os.path.join(root, f))
                if zip_fileext not in f:
                    try:
                        with open(os.path.join(root, f), 'rb') as f_in:
                            with gzip.open(
                                    os.path.join(root, f+zip_fileext),
                                    'wb',
                                    compresslevel=zip_compressionlevel) as f_out:
                                shutil.copyfileobj(f_in, f_out)

                    except Exception as e:
                        print("Error during zipping file {}".format(os.path.join(root, f)), e)
                        traceback.print_exc()
                    else:
                        os.remove(os.path.join(root, f))


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
            return os.path.relpath(pathname, os.path.join(os.environ['HOME'],
                self.args.archive))
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







def main(args):
    #FUSE(WorkdirFS(root), mountpoint, nothreads=True, foreground=True)
    # start FUSE filesystem
    FUSE(WorkdirFS(args), os.path.join(os.environ['HOME'], args.mountpoint), nothreads=True, foreground=True)

if __name__ == '__main__':
    #main(sys.argv[2], sys.argv[1])
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--archive",
            default='archive/workdir', help="Path to archivedir-base")
    parser.add_argument("-m", "--mountpoint",
            default='Work', help='Path to Workdir')
    parser.add_argument("-t", "--timeoffset", type=int, default=2, help="""If you're working
            all day till 3 o'clock in the morning, set it to 4, so next day
            archive-dir will be created 4 hours after midnight. You have 1h
            tolerance, if you're working one day a little bit longer""")
    parser.add_argument("-Y", "--yearlydir", action="store_true")
    parser.add_argument("-M", "--monthlydir", action="store_true")
    parser.add_argument("-W", "--weeklydir", action="store_true")
    args = parser.parse_args()
    print(args)
    #root = os.environ['HOME']+'/archive'
    #mountpoint = os.environ['HOME']+'/Work'
    main(args)
