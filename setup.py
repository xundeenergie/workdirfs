from setuptools import setup

setup(name='workdirfs',
      version='0.1',
      description='Workdir Filesystem in Userspace (FUSE)',
      url='http://github.com/xundeenergie/workdirfs.git',
      author='Jakobus Schürz',
      author_email='jakob@schuerz.at',
      license='MIT',
      packages=['workdirfs'],
      install_requires=[
          'fusepy',
      ],
      zip_safe=False)
