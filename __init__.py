# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SIREN
                                 A QGIS plugin
 SIREN Plugin
                             -------------------
        begin                : 2017-01-05
        copyright            : (C) 2017 by ONEMA
        email                : contact@collombj.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SIREN class from file SIREN.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .SIREN import SIREN
    return SIREN(iface)
