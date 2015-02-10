from __future__ import print_function

from os.path import dirname, exists, join
import sys, subprocess
from setuptools import setup

setup_dir = dirname(__file__)
git_dir = join(setup_dir, '.git')
base_package = 'webdash'
version_file = join(setup_dir, base_package, 'version.py')

# Automatically generate a version.py based on the git version
if exists(git_dir):
    p = subprocess.Popen(["git", "describe", "--tags", "--long", "--dirty=-dirty"],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = p.communicate()
    # Make sure the git version has at least one tag
    if err:
        print("Error: You need to create a tag for this repo to use the builder")
        sys.exit(1)

    # Convert git version to PEP440 compliant version
    # - Older versions of pip choke on local identifiers, so we can't include the git commit
    v, commits, local = out.decode('utf-8').rstrip().split('-', 2)
    if commits != '0' or '-dirty' in local:
        v = '%s.post0.dev%s' % (v, commits)

    # Create the version.py file
    with open(version_file, 'w') as fp:
        fp.write("# Autogenerated by setup.py\n__version__ = '{0}'".format(v))

with open(version_file, 'r') as fp:
    exec(fp.read(), globals())

with open(join(setup_dir, 'README.rst'), 'r') as readme_file:
    long_description = readme_file.read()

setup(
    name='roborio-webdash',
    version=__version__,
    description='A web-based dashboard with several useful utilities',
    long_description=long_description,
    author='Christian Balcom',
    author_email='robot.inventor@gmail.com',
    keywords='frc first robotics networktables netconsole livewindow',
    packages=[base_package],
    include_package_data=True,
    license='BSD License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License'
    ],
    entry_points={
        'console_scripts': [
            'webdash=webdash.main:main',
        ],
    }
)