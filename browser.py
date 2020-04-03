import struct
from enigma import eConsoleAppContainer
from Components.VolumeControl import VolumeControl
import datasocket

class Browser:
    def __init__(self, urlcallback = None):
        self.onBroadcastPlay = []
        self.onBroadcastStop = []
        self.onExit = []
        self.commandserver = None

    def connectedClients(self):
        return self.commandserver.connectedClients()

    def start(self, url, onid, tsid, sid):
        if not self.commandserver:
            self.commandserver = datasocket.CommandServer()
            datasocket.onCommandReceived.append(self.onCommandReceived)
            datasocket.onBrowserClosed.append(self.onBrowserClosed)
            container = eConsoleAppContainer()
            container.execute("/usr/bin/openhbbtvbrowser %s --onid %d --tsid %d --sid %d" % (url, onid, tsid, sid))

    def stop(self):
        if self.commandserver:
            self.commandserver = None

    def onCommandReceived(self, cmd, data):
        if cmd == 1:
            for x in self.onBroadcastPlay:
                x()
        elif cmd == 2:
            for x in self.onBroadcastStop:
                x()
        elif cmd == 3:
            VolumeControl.instance and VolumeControl.instance.volMute()
        elif cmd == 4:
            VolumeControl.instance and VolumeControl.instance.volDown()
        elif cmd == 5:
            VolumeControl.instance and VolumeControl.instance.volUp()
        elif cmd == 6:
            for x in self.onExit:
                x()

    def onBrowserClosed(self):
        self.commandserver = None
        for x in self.onExit:
            x()
