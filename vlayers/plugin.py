# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : DB Manager
Description          : Database manager plugin for QGIS
Date                 : May 23, 2011
copyright            : (C) 2011 by Giuseppe Sucameli
email                : brush.tyler@gmail.com

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# this will disable the dbplugin if the connector raise an ImportError
from .connector import VLayerConnector

from PyQt4.QtCore import Qt, QSettings, QUrl
from PyQt4.QtGui import QIcon, QApplication, QAction
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry
from qgis.gui import QgsMessageBar

from ..plugin import DBPlugin, Database, Table, VectorTable, RasterTable, TableField, TableIndex, TableTrigger, InvalidDataException
try:
        from . import resources_rc
except ImportError:
        pass



def classFactory():
    return VLayerDBPlugin

class VLayerDBPlugin(DBPlugin):

        @classmethod
        def icon(self):
            return QIcon(":/db_manager/vlayers/icon")

        @classmethod
        def typeName(self):
            return 'vlayers'

        @classmethod
        def typeNameString(self):
            return 'Virtual Layers'

        @classmethod
        def providerName(self):
            return 'virtual'

        @classmethod
        def connectionSettingsKey(self):
            return 'vlayers'

        @classmethod
        def connections(self):
            return [VLayerDBPlugin('QGIS layers')]

        def databasesFactory(self, connection, uri):
            return FakeDatabase(connection, uri)

        def database( self ):
            return self.db

        #def info( self ):

        def connect(self, parent=None):
            self.connectToUri( "qgis" )
            return True


class FakeDatabase(Database):
        def __init__(self, connection, uri):
            Database.__init__(self, connection, uri)

        def connectorsFactory(self, uri):
            return VLayerConnector(uri)


        def dataTablesFactory(self, row, db, schema=None):
            return LTable(row, db, schema)

        def vectorTablesFactory(self, row, db, schema=None):
            return LVectorTable(row, db, schema)

        def rasterTablesFactory(self, row, db, schema=None):
            return None


        def info(self):
                from .info_model import LDatabaseInfo
                return LDatabaseInfo(self)

        def sqlResultModel(self, sql, parent):
                from .data_model import LSqlResultModel
                return LSqlResultModel(self, sql, parent)

        def toSqlLayer(self, sql, geomCol, uniqueCol, layerName="QueryLayer", layerType=None, avoidSelectById=False):
            q = QUrl.toPercentEncoding(sql)
            s = "?query=%s" % q
            if uniqueCol is not None:
                s += "&uid=" + uniqueCol
            if geomCol is not None:
                s += "&geometry=" + geomCol
            return QgsVectorLayer(s, layerName, "virtual" )

        def registerDatabaseActions(self, mainWindow):
            return
        def runAction(self, action):
            return

        def uniqueIdFunction(self):
            return None

        def explicitSpatialIndex( self ):
            return True

        def spatialIndexClause( self, src_table, src_column, dest_table, dest_column ):
            return '"%s"._search_frame_ = "%s"."%s"' % (src_table,dest_table, dest_column)


class LTable(Table):
        def __init__(self, row, db, schema=None):
                Table.__init__(self, db, None)
                self.name, self.isView, self.isSysTable = row


        def tableFieldsFactory(self, row, table):
                return LTableField(row, table)

        def tableDataModel(self, parent):
                from .data_model import LTableDataModel
                return LTableDataModel(self, parent)

        def canBeAddedToCanvas( self ):
            return False


class LVectorTable(LTable, VectorTable):
        def __init__(self, row, db, schema=None):
            LTable.__init__(self, row[:-5], db, schema)
            VectorTable.__init__(self, db, schema)
            # SpatiaLite does case-insensitive checks for table names, but the
            # SL provider didn't do the same in QGis < 1.9, so self.geomTableName
            # stores the table name like stored in the geometry_columns table
            self.geomTableName, self.geomColumn, self.geomType, self.geomDim, self.srid = row[-5:]

        def uri(self):
                uri = self.database().uri()
                uri.setDataSource('', self.geomTableName, self.geomColumn)
                return uri

        def hasSpatialIndex(self, geom_column=None):
            return True

        def createSpatialIndex(self, geom_column=None):
            return

        def deleteSpatialIndex(self, geom_column=None):
            return

        def refreshTableEstimatedExtent(self):
            self.extent = self.database().connector.getTableExtent(("id",self.geomTableName), None)

        def runAction(self, action):
            return

        def toMapLayer(self):
            return QgsMapLayerRegistry.instance().mapLayer(self.geomTableName)

class LTableField(TableField):
        def __init__(self, row, table):
                TableField.__init__(self, table)
                self.num, self.name, self.dataType, self.notNull, self.default, self.primaryKey = row
                self.hasDefault = self.default

