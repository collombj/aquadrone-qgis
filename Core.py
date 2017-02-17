"""
Class dedicated to the layer management. This class also manage the Thread system
"""
import psycopg2
from qgis.PyQt import QtCore
from qgis._core import QgsDataSourceURI
from qgis._core import QgsMapLayerRegistry
from qgis._core import QgsVectorLayer

from ListenerWorker import ListenerWorker
from test.ErrorWindow import ErrorWindow


class Core:
    def __init__(self, host, port, username, password, database, ui):
        """
        Constructor the @Core class. It initialized everything necessary for the layer manipulation.
        :param host: The database hostname
        :param port: The database port
        :param username: The database username
        :param password: The database password
        :param database: The database name
        :param ui: The Iface (UI) reference (required to manipulate layers)
        """

        # Layer list manipulate by the connection
        self.layer = []

        # Notification key to detect change in DB
        # (see: https://www.postgresql.org/docs/9.1/static/sql-notify.html)
        self.notify_key = 'siren_key'

        # URI of the database. This information is required for the database connection in Layers
        self.uri = QgsDataSourceURI()

        if host == None:
            ErrorWindow("Erreur hote", "Veuillez indiquer l'hote dans les parametres de connexion")
        if port == None:
            ErrorWindow("Erreur port", "Veuillez indiquer le port dans les parametres de connexion")
        if username == None:
            ErrorWindow("Erreur username", "Veuillez indiquer le nom d'utilisation dans les parametres de connexion")
        if password == None:
            ErrorWindow("Erreur password", "Veuillez indiquer le mot de passe dans les parametres de connexion")
        if database == None:
            ErrorWindow("Erreur database", "Veuillez indiquer la base de donnees dans les parametres de connexion")

        # Set information for the layer URI
        self.uri.setConnection(host, port, database, username, password)

        # This connection is for the Notification system. It cannot be the previous one.
        # Indeed, the previous can only be manipulated by the QGIS layer system. If we need to
        # query the database with SQL request, a @Psycopg2 class is required.
        #
        # Important: The notify system is managed in another thread (a non-ui one). If the LISTEN system
        # is set into an UI thread, the UI will be slowed.
        self.conn = psycopg2.connect(dbname=database, user=username, password=password, host=host, port=port)
        # This option is required for the multi-threading.
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        # Init the notification worker
        self.worker = ListenerWorker(self.conn, self.notify_key)
        # Create the thread (a non-ui one)
        self.thread = QtCore.QThread(ui)

        # Initialize the notification system
        self.notify_init()

    def notify_init(self):
        """
        Method initializing the notification system, and start the associated thread.
        """
        # Create a cursor for the SQL query
        curs = self.conn.cursor()
        # Execute the Listen query. This query open a listener.
        # Warning: the current action do not wait for a notification.
        # You need to check manually for a new notification. (see @ListenerWorker.run())
        curs.execute('LISTEN ' + self.notify_key + ';')
        # Close the cursor to free memory
        curs.close()
        print
        'Waiting for notifications on channel ' + self.notify_key

        # Move the ListenerWorker to the thread (to avoid execution into the UI thread)
        self.worker.moveToThread(self.thread)
        # Listen for thread notification about progression
        # In reality, it is just a notification to indicate a refresh. The method in parameter
        # take a float. This float is the progression (in percent). In our case, the percentage only represent the
        # the notification situation (0 : it is OK ; -1 : it is problem)
        self.worker.progress.connect(self.refresh)
        # Specify the method to launch (the run action)
        self.thread.started.connect(self.worker.run)
        # Start the thread
        self.thread.start()

    def corrected_layer(self):
        """
        Display the Corrected Layer
        """
        self.display_layer('location_corrected')

    def difference_layer(self):
        """
        Display the Difference Layer
        """
        self.display_layer('location_difference')

    def brut_layer(self):
        """
        Display the brut Layer
        """
        self.display_layer('location_brut')

    def display_layer(self, layer_name):
        """
        Display a player passed in params into the current QGIS project.
        The layer_name is the column to find in measures_displayed View.
        The layer_name is also used for the layer name in the QGIS project.
        :param layer_name: The Column name to display.
        """
        # Specify the view and the column to use for the layer
        self.uri.setDataSource('public', 'measure_formated', layer_name)
        # Specify the primary key of the entries. For the record, the only unique column is measure_id
        self.uri.setKeyColumn('measure_id')

        # Create a layer based on the information previously specified (database and column). The layer is
        # not yet added to the UI. The layer is a Postgres type
        layer = QgsVectorLayer(self.uri.uri(), layer_name, 'postgres')
        # Check if the Layer is valid or not (in case of the column/table/... does not exist
        if not layer.isValid():
            print
            'Layer [' + layer_name + '] failed to load!'
            return

        # Save the layer into the layer list (reminder: the layer list is useful to refresh all layers when
        # a notification is received)
        self.layer.append(layer)

        # Add the created layer to the QGIS project
        QgsMapLayerRegistry.instance().addMapLayer(layer)

    def remove_corrected_layer(self):
        """
        Remove the layer of corrected positions
        :return:
        """
        self.remove_layer('location_corrected')

    def remove_difference_layer(self):
        """
        Remove the difference layer
        :return:
        """
        self.remove_layer('location_difference')

    def remove_brut_layer(self):
        """
        Remove the layer of raw positions
        :return:
        """
        self.remove_layer('location_brut')

    def remove_layer(self, layer_name):
        """
        Remove a layer from the canvas and the legend, if it exists
        :param layer_name:
        :return:
        """
        for layer in QgsMapLayerRegistry.instance().mapLayers():
            if layer.find(layer_name) != -1:
                QgsMapLayerRegistry.instance().removeMapLayer(layer)

    def stop(self):
        """
        Method to stop the automatic refresh (the dedicated thread)
        """

        # Kill the thread
        self.worker.kill()

        # Unlisten the notification
        curs = self.conn.cursor()
        curs.execute('UNLISTEN ' + self.notify_key + ';')
        curs.close()

        # Close the whole SQL connection (dedicated to the Notification system)
        self.conn.close()  # WARNING: If a crash appears on module reload, it could be that line

    def refresh(self, code):
        """
        Method to refresh layers registered in @Core.layer array.
        :param code: The refresh code (It cannot be a boolean due to Thread restriction cf. @Core.notify_init())
                     The refresh code could be : 0 if the refresh should be done, another value is to avoid a refresh.
        """
        if code != 0:
            return

        print
        'Refresh in progress...'

        for layer in self.layer:
            # refresh the layer
            layer.setCacheImage(None)
            layer.triggerRepaint()
