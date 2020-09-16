from __future__ import absolute_import
from Screens.Screen import Screen
from enigma import eTimer, fbClass, eRCInput
import os
from .browser import Browser

browserinstance = None
g_session = None


class HbbTVWindow(Screen):
    skin = """
        <screen name="HbbTVWindow" position="0,0" size="1280,720" backgroundColor="transparent" flags="wfNoBorder" title="HbbTV Plugin">
        </screen>
        """

    def __init__(self, session, url=None, onid=0, tsid=0, sid=0):
        Screen.__init__(self, session)

        global g_session
        g_session = session
        self._url = url
        self.closetimer = eTimer()
        self.closetimer.callback.append(self.stop_hbbtv_application)
        self.starttimer = eTimer()
        self.starttimer.callback.append(self.start_hbbtv_application)
        self.starttimer.start(100)
        self.count = 0
        self.onid = onid
        self.tsid = tsid
        self.sid = sid
        self.lastservice = self.session.nav.getCurrentlyPlayingServiceReference()

        global browserinstance
        if not browserinstance:
            browserinstance = Browser()
        browserinstance.start(self._url, self.onid, self.tsid, self.sid)

    def start_hbbtv_application(self):
        global browserinstance
        if browserinstance.connectedClients() == 0:
            self.count += 1
            if self.count > 50:
                self.close()
            return

        self.starttimer.stop()
        fbClass.getInstance().lock()
        eRCInput.getInstance().lock()

        browserinstance.onBroadcastPlay.append(self.onBroadcastPlay)
        browserinstance.onBroadcastStop.append(self.onBroadcastStop)
        browserinstance.onExit.append(self.onExit)

    def stop_hbbtv_application(self):
        self.closetimer.stop()
        self.closetimer = None
        self.close()

    def onBroadcastPlay(self):
        # TODO:
        # ffmpeg -i http://127.0.0.1:8001/1:0:19:2B66:3F3:1:C00000:0:0:0: -window_size 10 -extra_window_size 10 -use_template 1 -use_timeline 1 -f dash -c:v copy -vtag avc1 -streaming 1 -remove_at_exit 1 manifest.mpd
        # python -m SimpleHTTPServer | python3 -m http.server
        global g_session
        g_session.nav.playService(self.lastservice)

    def onBroadcastStop(self):
        # TODO:
        # ffmpeg
        global g_session
        g_session.nav.stopService()

    def onExit(self):
        fbClass.getInstance().unlock()
        eRCInput.getInstance().unlock()
        global browserinstance
        browserinstance.onBroadcastPlay.remove(self.onBroadcastPlay)
        browserinstance.onBroadcastStop.remove(self.onBroadcastStop)
        browserinstance.onExit.remove(self.onExit)
        global g_session
        g_session.nav.stopService()
        g_session.nav.playService(self.lastservice)
        self.close()
