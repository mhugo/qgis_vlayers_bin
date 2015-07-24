QGIS virtual layers
-------------------

1/ Choose the correct architecture (win32/win64) and qgis version (2.8/2.10) combination
and copy the two .dll files in your 'plugins' directory of the QGIS installation.
For example in C:\OSGEO4W\apps\qgis\plugins

2/ Copy the 'vlayer' directory into python\plugins\db_manager\db_plugins
For example in C:\OSGEO4W\apps\qgis\python\plugins\db_manager\db_plugins

It should be installed aside existing 'spatialite' and 'postgis' directories

Launch QGIS, enable 'Virtual layer plugin' in the plugin menu.

