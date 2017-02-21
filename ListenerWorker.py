"""
Class representing the thread system to listen database notification. When a notification is received, the callable set
for the progress update is triggered.
"""
import select

from qgis.PyQt import QtCore


class ListenerWorker(QtCore.QObject):
    def __init__(self, conn, notify_key):
        """
        Constructor for the ListenerWorker. It required the psycopg2 connection and the notification key (string).
        :param conn: The psycopg2 connection to the server. It is required to listen notification.
        :param notify_key: The notification to wait for
        """

        # Call the parent constructor
        QtCore.QObject.__init__(self)

        # Field: notification key
        self.notify_key = notify_key
        # Field: psycopg2 connection
        self.conn = conn

        # Boolean to know if the thread is killed or not
        self.killed = False

    def run(self):
        """
        Run action. It is listening for new notification (specially for the notify_key one)
        """

        # Try-except is only to avoid a crash on reload due to async conn close.
        # It could be improve with full exception management
        try:
            while not self.killed:
                # Wait and retrieve an event appears onto the SQL connection
                if not select.select([self.conn], [], [], 10) == ([], [], []):  # 10 is for the timeout in seconds
                    self.conn.poll()  # Get back the information waiting onto the SQL connection
                    while self.conn.notifies:  # Iterate on all waiting notification
                        notify = self.conn.notifies.pop(0)  # Get the last insert notification
                        # Trigger the refresh only if the notification is the notify_key
                        if notify.channel == self.notify_key:
                            # Emit a progress notification
                            # The progress notification is only used to trigger the refresh
                            self.progress.emit(0)
                            print("received notification from dabatabase")
        except:
            pass

        # When the notification listening is over, trig the progress status with finish. Do not require layers refresh.
        # To not refresh and kill properly the thread, send a -1 value to the refresh method (via the finished)
        self.finished.emit(-1)

    def kill(self):
        """
        Method to stop the thread.
        """
        self.killed = True

    # Use default method for the finished, error and progress methods (it call the associated callable - refresh - with
    # a float in param
    finished = QtCore.pyqtSignal(object)
    error = QtCore.pyqtSignal(Exception, basestring)
    progress = QtCore.pyqtSignal(float)
