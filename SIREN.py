# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SIREN
                    Main Class. This class is the UI loader
 SIREN Plugin
                              -------------------
        begin                : 2017-01-05
        git sha              : $Format:%H$
        copyright            : (C) 2017 by ONEMA
        email                : contact@collombj.com
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
import os.path

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon

import resources
from Core import Core
from ErrorWindow import ErrorWindow
from SIREN_dockwidget import SIRENDockWidget


class SIREN:
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Edit part for the plugin (Init the classes members)
        self.database_connection = None  # Database list (will be initialized in @SIREN::init_database_selector()
        self.core = None  # Main class to manipulate Layers and Notifications

        # End of Edit part

        self.iface = iface

        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SIREN_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        self.actions = []
        self.menu = self.tr(u'&SIREN')
        self.toolbar = self.iface.addToolBar(u'SIREN')
        self.toolbar.setObjectName(u'SIREN')
        self.pluginIsActive = False
        self.dockwidget = None

        # Automatically Display the Widget
        self.run()

    # Automatically Generated
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SIREN', message)

    # Automatically Generated
    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)
        self.actions.append(action)
        return action

    # Automatically Generated
    def initGui(self):
        icon_path = ':/plugins/SIREN/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())

    def onClosePlugin(self):
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        self.pluginIsActive = False

        # Stop the Multi-threading (managed by the Main Class @Core
        if self.core is not None:
            self.core.reset()

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&SIREN'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    # --------------------------------------------------------------------------

    def run(self):

        if not self.pluginIsActive:
            # Read the param list stored in QGIS.
            # Only entries starting with #PostgreSQL/connections#
            self.database_connection = QSettings()

            self.pluginIsActive = True
            if self.dockwidget is None:
                self.dockwidget = SIRENDockWidget()
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # Initialize the Database list in the UI
            self.init_database_selector()
            # Associate method @SIREN.live_button to the button click (UI - Live)
            self.dockwidget.liveButton.clicked.connect(self.live_button)
            # Associate method @SIREN.reset_button to the button click (UI - Live)
            self.dockwidget.resetButton.clicked.connect(self.reset_button)

            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

    def init_database_selector(self):
        """
        Method to initialize the Database selector.
        This method load all information and display it into the UI selector.
        """
        # Restrict the list to Postgres connections
        self.database_connection.beginGroup('PostgreSQL/connections')

        # Create a set for the connection list
        connector_name = set()
        for entry in sorted(self.database_connection.allKeys()):
            # Take only the information before the "/". It is the connector name
            connector_name.add(entry.split('/')[0])

        # There is a 'selected' Key. It is not entered by the user, so delete it (if exist)
        connector_name.discard('selected')
        # Clear the list in the UI selector
        self.dockwidget.databaseSelector.clear()
        # Populate the UI selector with new entries
        for entry in sorted(list(connector_name)):
            self.dockwidget.databaseSelector.addItem(entry)

    def live_button(self):
        """
        Action triggered when the 'live' button is pressed
        """
        self.dockwidget.liveButton.setEnabled(False)

        # if no layer do nothing
        if not self.dockwidget.checkBoxCorrected.isChecked():
            if not self.dockwidget.checkBoxDifference.isChecked():
                if not self.dockwidget.checkBoxBrut.isChecked():
                    ErrorWindow("Erreur selection couche", "Veillez selectionner une couche avant de continuer",
                                "critical")
                    #enable live_button
                    self.dockwidget.liveButton.setEnabled(True)
                    return

        # init core
        if self.core is None:
            # Get the current database selection (in the UI selector)
            selected = self.dockwidget.databaseSelector.currentText()
            if selected == "":
                ErrorWindow("Erreur selection base de donnees",
                            "Veillez selectionner une base de donnees avant de valider",
                            "information")

                # enable live_button
                self.dockwidget.liveButton.setEnabled(True)
                return

            # Construct the @Core class (Main Class)
            # The Class need the global information of the database
            # The Class need to manipulate layers so a reference to the interface (iface) is required
            self.core = Core(
                self.database_connection.value(selected + '/host'),
                self.database_connection.value(selected + '/port'),
                self.database_connection.value(selected + '/username'),
                self.database_connection.value(selected + '/password'),
                self.database_connection.value(selected + '/database'),
                self.iface
            )

        self.core.connect_init()

        self.update_layer_list()
        print("live -> stop")
        # unbind live event
        self.dockwidget.liveButton.clicked.disconnect(self.live_button)
        # change text
        self.dockwidget.liveButton.setText("Stop")
        # bind stop event
        self.dockwidget.liveButton.clicked.connect(self.stop_button)
        # enable liveButton
        self.dockwidget.liveButton.setEnabled(True)
        # disable resetButton
        self.dockwidget.resetButton.setEnabled(False)

    def stop_button(self):
        """
        Stop listening
        :return:
        """
        # set inactive
        self.dockwidget.liveButton.setEnabled(False)
        print("stop -> live")
        self.core.stop()
        # change text
        self.dockwidget.liveButton.setText("Live")

        # unbind stop event
        self.dockwidget.liveButton.clicked.disconnect(self.stop_button)
        # bind live event
        self.dockwidget.liveButton.clicked.connect(self.live_button)
        # setactive
        self.dockwidget.liveButton.setEnabled(True)
        # enable resetButton
        self.dockwidget.resetButton.setEnabled(True)

    def reset_button(self):
        """
        Reset stuff
        """
        self.dockwidget.liveButton.setEnabled(False)
        print("reset")
        # remove all the layers we added
        self.core.reset()
        self.uncheck_checkboxes()
        # destroys core
        self.core = None
        #enable liveButton
        self.dockwidget.liveButton.setEnabled(True)
        # disable resetButton
        self.dockwidget.resetButton.setEnabled(False)

    def update_layer_list(self):
        """
        TODO
        :return:
        """
        # If the 'Brut Position' checkbox is checked add the associated layer to the current project
        if self.dockwidget.checkBoxBrut.isChecked():
            self.core.brut_layer()
        else:
            self.core.remove_brut_layer()

        # If the 'Corrected Position' checkbox is checked add the associated layer to the current project
        if self.dockwidget.checkBoxCorrected.isChecked():
            self.core.corrected_layer()
        else:
            self.core.remove_corrected_layer()

        # If the 'Difference Area' checkbox is checked add the associated layer to the current project
        if self.dockwidget.checkBoxDifference.isChecked():
            self.core.difference_layer()
        else:
            self.core.remove_difference_layer()


    def uncheck_checkboxes(self):
        """
        TODO
        :return:
        """
        self.dockwidget.checkBoxBrut.setChecked(False)
        self.dockwidget.checkBoxCorrected.setChecked(False)
        self.dockwidget.checkBoxDifference.setChecked(False)
