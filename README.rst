RoboRIO WebDash
===============

This is a web-based dashboard, designed to be run on the LabVIEW RoboRIO, for
collecting and displaying diagnostic data from Netconsole, Network Tables, and
Live Window. Once installed, it provides an elegant web ui that can be accessed
at port 5801 on your RoboRIO.

Installation
============

RoboRIO Webdash can be installed with pip, or with the robotpy installer.

With the robotpy installer
::

   #Connected to internet
   python3 installer.py download roborio-webdash

   #Connected to RoboRIO
   python3 installer.py install roborio-webdash

Or with pip
::

   pip install roborio-webdash

Once installed, run the following command as admin on the RoboRIO to install the dashboard's init script and set the dashboard to run at boot.

::

   webdash install-initfile

License
=======

See LICENSE.txt

Authors
=======

Christian Balcom (robot.inventor@gmail.com, FRC Team 4819)