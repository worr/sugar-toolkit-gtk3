# Copyright (C) 2013 Daniel Narvaez
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import json
import os

from gi.repository import GConf
from gi.repository import WebKit2
from gwebsockets.server import Server

from sugar3.activity import activity


class ActivityAPI:
    def __init__(self, activity):
        self._activity = activity

    def get_xo_color(self):
        client = GConf.Client.get_default()
        color_string = client.get_string('/desktop/sugar/user/color')
        return color_string.split(",")

    def close(self):
        self._activity.close()


class HTMLActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self._web_view = WebKit2.WebView()
        self.set_canvas(self._web_view)
        self._web_view.show()

        self._authenticated = False

        self._server = Server()
        self._server.connect("session-started", self._session_started_cb)
        port = self._server.start()

        index_path = os.path.join(activity.get_bundle_path(), "index.html")
        self._key = os.urandom(16).encode("hex")
        self._web_view.load_uri("file://%s?port=%s&key=%s" %
                                (index_path, port, self._key))

        self._apis = {}
        self._apis["activity"] = ActivityAPI(self)

    def _session_started_cb(self, server, session):
        session.connect("message-received", self._message_received_cb)

    def _message_received_cb(self, session, message):
        request = json.loads(message.data)

        if request["method"] == "authenticate":
            if self._key == request["params"][0]:
                self._authenticated = True
                return

        if not self._authenticated:
            return

        api_name, method_name = request["method"].split(".")
        method = getattr(self._apis[api_name], method_name)

        result = method(*request["params"])

        response = {"result": result,
                    "error": None,
                    "id": request["id"]}

        session.send_message(json.dumps(response))
