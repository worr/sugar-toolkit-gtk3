# Copyright (C) 2007, One Laptop Per Child
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
import sys
import logging

import gobject
import gtk
import hippo

class Popup(hippo.CanvasBox, hippo.CanvasItem):
    __gtype_name__ = 'SugarPopup'

    __gsignals__ = {
        'action-completed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ([]))
    }

    def __init__(self):
        hippo.CanvasBox.__init__(self)
        self._window = None
        self.connect('button-press-event', self._button_press_event_cb)

    def popup(self, x, y):
        if not self._window:
            self._window = hippo.CanvasWindow(gtk.WINDOW_POPUP)
            self._window.move(x, y)
            self._window.set_root(self)
            self._window.show()

    def popdown(self):
        if self._window:
            self._window.destroy()
            self._window = None

    def _button_press_event_cb(self, menu, event):
        self.emit('action-completed')
