from __future__ import absolute_import
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.InfoBar import InfoBar
from Components.ServiceEventTracker import ServiceEventTracker
from enigma import iPlayableService, iServiceInformation
from .hbbtv import HbbTVWindow


class HBBTVParser(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.started = False
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.serviceStarted})
        self.openUrl = False

    def serviceStarted(self):
        if self.started:
            return
        if InfoBar.instance:
            InfoBar.instance.onHBBTVActivation.append(self.onHBBTVActivation)
            self.started = True

    def onHBBTVActivation(self):
        service = self.session.nav.getCurrentService()
        info = service and service.info()
        url = info and info.getInfoString(iServiceInformation.sHBBTVUrl) or False
        onid = info and info.getInfo(iServiceInformation.sONID) or -1
        tsid = info and info.getInfo(iServiceInformation.sTSID) or -1
        sid = info and info.getInfo(iServiceInformation.sSID) or -1

        self.openUrl = url
        if not self.openUrl:
            self.close()
            return
        self.session.open(HbbTVWindow, self.openUrl, onid, tsid, sid)


def autostart(reason, **kwargs):
    if 'session' in kwargs:
        HBBTVParser(kwargs['session'])


def Plugins(**kwargs):
    return PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart)
