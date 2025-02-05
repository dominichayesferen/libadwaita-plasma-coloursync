
from gi.repository import Adw
from gi.repository import Gtk

@Gtk.Template(resource_path='/io/github/dominichayesferen/libadwaitareload/window.ui')
class LibadwaitareloadWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'LibadwaitareloadWindow'

    label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
