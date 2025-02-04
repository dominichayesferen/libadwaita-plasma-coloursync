#!/usr/bin/python3
import os
import math
import dbus
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop

gtkcssfile = os.path.expanduser("~") + "/.config/gtk-4.0/gtk.css"

class dbouos:
    def __init__(self):
        self.themePreferenceChanged("org.kde.kdeglobals.General", "ColorScheme", "")
        mainloop = DBusGMainLoop()
        self.interface = dbus.SessionBus(mainloop=mainloop).get_object("org.freedesktop.portal.Desktop", "/org/freedesktop/portal/desktop")
        self.interface = dbus.Interface(self.interface, "org.freedesktop.portal.Settings")
        self.interface.connect_to_signal('SettingChanged', self.themePreferenceChanged)


    def color_is_light(self, redc, greenc, bluec):
        #Returns:
        # True: Light
        # False: Dark
        rSRGB = redc / 255
        gSRGB = greenc / 255
        bSRGB = bluec / 255

        r = rSRGB / 12.92 if rSRGB <= .03928 else math.pow((rSRGB + .055) / 1.055, 2.4)
        g = gSRGB / 12.92 if rSRGB <= .03928 else math.pow((gSRGB + .055) / 1.055, 2.4)
        b = rSRGB / 12.92 if bSRGB <= .03928 else math.pow((bSRGB + .055) / 1.055, 2.4)
        lumi = .2126 * r + .7152 * g + .0722 * b

        if lumi > 0.5:
            return True
        else:
            return False


    def hextorrrgggbbb(self, hexcode):
        if hexcode == "#" or (len(hexcode) != 4 and len(hexcode) != 7):
            #You forgot CS Source!
            return "255,0,255"
        #Expand 3-digit colour codes to 6-digit ones
        if len(hexcode) == 4:
            hexcode = "#0" + hexcode[1] + "0" + hexcode[2] + "0" + hexcode[3]
        r, g, b = tuple(int(hexcode[i:i+2], 16) for i in (1, 3, 5)) #Dodge the # character
        return "%s,%s,%s" % (r, g, b)


    def themePreferenceChanged(self, path, intent, value):
        if path != "org.kde.kdeglobals.General" or intent != "ColorScheme":
            return #Ignore other signals
        #Open file for writing
        if os.path.exists(gtkcssfile):
            with open(gtkcssfile, 'r') as fp:
                result = fp.read().splitlines()
        else:
            result = []
        #Remove current colour values
        for i in ["accent_color", "accent_bg_color", "accent_fg_color", "destructive_color", "destructive_bg_color", "destructive_fg_color", "success_color", "success_bg_color", "success_fg_color", "warning_color", "warning_bg_color", "warning_fg_color", "error_color", "error_bg_color", "error_fg_color", "window_bg_color", "window_fg_color", "view_bg_color", "view_fg_color", "sidebar_bg_color", "sidebar_fg_color", "sidebar_backdrop_color", "sidebar_shade_color", "secondary_sidebar_bg_color", "secondary_sidebar_fg_color", "secondary_sidebar_backdrop_color", "secondary_sidebar_shade_color", "headerbar_bg_color", "headerbar_fg_color", "headerbar_border_color", "headerbar_backdrop_color", "headerbar_shade_color", "card_bg_color", "card_fg_color", "card_shade_color", "thumbnail_bg_color", "thumbnail_fg_color", "dialog_bg_color", "dialog_fg_color", "popover_bg_color", "popover_fg_color", "shade_color", "scrollbar_outline_color"]:
            count = 0
            for line in result:
                if line.startswith("@define-color " + i) and line.endswith(";"):
                    result.pop(count)
                count += 1
        #Get the colour palette from kdeglobals
        with open(os.path.expanduser("~") + "/.config/kdeglobals", 'r') as fp:
            colscm = {"[Colors:Header]": {}, "[Colors:Header][Inactive]": {}, "[Colors:Selection]": {}, "[Colors:Selection]": {}, "[Colors:View]": {}, "[Colors:Window]": {}, "[WM]": {}}
            currentsection = ""
            count = 0
            for i in fp.read().splitlines():
                if i.startswith("[") and i.endswith("]"):
                    currentsection = i
                else:
                    if currentsection in colscm and not i == "":
                        if "," in i.split("=")[1] or i.split("=")[1].startswith("#"):
                            name = i.split("=")[0]
                            if i.split("=")[1].startswith("#"):
                                value = self.hextorrrgggbbb(i.split("=")[1])
                            else:
                                value = ",".join(i.split("=")[1].split(",")[:3])
                            colscm[currentsection][name] = value
        #Change gtk-4.0 gtk.css obviously
        argr, argg, argb = colscm["[Colors:Window]"]["BackgroundNormal"].split(",")
        darkmode = not self.color_is_light(int(argr), int(argg), int(argb))
        # Accent Colours
        result.insert(0, "@define-color accent_color rgb(" + colscm["[Colors:Selection]"]["BackgroundNormal"] + ");")
        result.insert(1, "@define-color accent_bg_color rgb(" + colscm["[Colors:Selection]"]["BackgroundNormal"] + ");")
        result.insert(2, "@define-color accent_fg_color rgb(" + colscm["[Colors:Selection]"]["ForegroundNormal"] + ");")
        # Destructive
        result.insert(3, "@define-color destructive_color rgb(" + colscm["[Colors:Window]"]["ForegroundNegative"] + ");")
        result.insert(4, "@define-color destructive_bg_color rgb(" + colscm["[Colors:Window]"]["ForegroundNegative"] + ");")
        result.insert(5, "@define-color destructive_fg_color #FFF;")
        # Success
        result.insert(6, "@define-color success_color rgb(" + colscm["[Colors:Window]"]["ForegroundPositive"] + ");")
        result.insert(7, "@define-color success_bg_color rgb(" + colscm["[Colors:Window]"]["ForegroundPositive"] + ");")
        result.insert(8, "@define-color success_fg_color #FFF;")
        # Warning
        result.insert(9, "@define-color warning_color rgb(" + colscm["[Colors:Window]"]["ForegroundNeutral"] + ");")
        result.insert(10, "@define-color warning_bg_color rgb(" + colscm["[Colors:Window]"]["ForegroundNeutral"] + ");")
        result.insert(11, "@define-color warning_fg_color #FFF;")
        # Error
        result.insert(12, "@define-color error_color rgb(" + colscm["[Colors:Window]"]["ForegroundNegative"] + ");")
        result.insert(13, "@define-color error_bg_color rgb(" + colscm["[Colors:Window]"]["ForegroundNegative"] + ");")
        result.insert(14, "@define-color error_fg_color #FFF;")
        # Windows
        result.insert(15, "@define-color window_bg_color rgb(" + colscm["[Colors:Window]"]["BackgroundNormal"] + ");")
        result.insert(16, "@define-color window_fg_color rgb(" + colscm["[Colors:Window]"]["ForegroundNormal"] + ");")
        # View
        result.insert(17, "@define-color view_bg_color rgb(" + colscm["[Colors:View]"]["BackgroundNormal"] + ");")
        result.insert(18, "@define-color view_fg_color rgb(" + colscm["[Colors:View]"]["ForegroundNormal"] + ");")
        # Sidebars
        result.insert(19, "@define-color sidebar_bg_color rgb(" + colscm["[Colors:View]"]["BackgroundNormal"] + ");")
        result.insert(20, "@define-color sidebar_fg_color rgb(" + colscm["[Colors:View]"]["ForegroundNormal"] + ");")
        result.insert(21, "@define-color sidebar_backdrop_color rgb(" + colscm["[Colors:View]"]["BackgroundNormal"] + ");")
        result.insert(22, "@define-color sidebar_shade_color rgba("+ colscm["[Colors:View]"]["ForegroundNormal"] + ",0.09);")
        # Secondary Sidebars
        result.insert(23, "@define-color secondary_sidebar_bg_color rgb(" + colscm["[Colors:View]"]["BackgroundNormal"] + ");")
        result.insert(24, "@define-color secondary_sidebar_fg_color rgb(" + colscm["[Colors:View]"]["ForegroundNormal"] + ");")
        result.insert(25, "@define-color secondary_sidebar_backdrop_color rgb(" + colscm["[Colors:View]"]["BackgroundNormal"] + ");")
        result.insert(26, "@define-color secondary_sidebar_shade_color rgba("+ colscm["[Colors:View]"]["ForegroundNormal"] + ",0.09);")
        # Headerbars
        if colscm["[Colors:Header]"] != {} and colscm["[Colors:Header][Inactive]"] != {}:
            result.insert(27, "@define-color headerbar_bg_color rgb(" + colscm["[Colors:Header]"]["BackgroundNormal"] + ");")
            result.insert(28, "@define-color headerbar_fg_color rgb(" + colscm["[Colors:Header]"]["ForegroundNormal"] + ");")
            result.insert(29, "@define-color headerbar_border_color rgb(" + colscm["[Colors:Header]"]["ForegroundNormal"] + ");")
            result.insert(30, "@define-color headerbar_backdrop_color rgb(" + colscm["[Colors:Header][Inactive]"]["BackgroundNormal"] + ");")
            result.insert(31, "@define-color headerbar_shade_color rgba("+ colscm["[Colors:Header]"]["ForegroundNormal"] + ",0.09);")
        else:
            result.insert(27, "@define-color headerbar_bg_color rgb(" + colscm["[WM]"]["activeBackground"] + ");")
            result.insert(28, "@define-color headerbar_fg_color rgb(" + colscm["[WM]"]["activeForeground"] + ");")
            result.insert(29, "@define-color headerbar_border_color rgb(" + colscm["[WM]"]["activeForeground"] + ");")
            result.insert(30, "@define-color headerbar_backdrop_color rgb(" + colscm["[WM]"]["inactiveBackground"] + ");")
            result.insert(31, "@define-color headerbar_shade_color rgba("+ colscm["[WM]"]["activeForeground"] + ",0.09);")
        # Cards
        result.insert(32, "@define-color card_bg_color rgb(" + colscm["[Colors:View]"]["BackgroundNormal"] + ");")
        result.insert(33, "@define-color card_fg_color rgb(" + colscm["[Colors:View]"]["ForegroundNormal"] + ");")
        result.insert(34, "@define-color card_shade_color rgba("+ colscm["[Colors:View]"]["ForegroundNormal"] + ",0.09);")
        # Thumbnails
        result.insert(35, "@define-color thumbnail_bg_color rgb(" + colscm["[Colors:View]"]["BackgroundNormal"] + ");")
        result.insert(36, "@define-color thumbnail_fg_color rgb(" + colscm["[Colors:View]"]["ForegroundNormal"] + ");")
        # Dialogs
        result.insert(37, "@define-color dialog_bg_color rgb(" + colscm["[Colors:Window]"]["BackgroundNormal"] + ");")
        result.insert(38, "@define-color dialog_fg_color rgb(" + colscm["[Colors:Window]"]["ForegroundNormal"] + ");")
        # Popovers
        result.insert(39, "@define-color popover_bg_color rgb(" + colscm["[Colors:View]"]["BackgroundNormal"] + ");")
        result.insert(40, "@define-color popover_fg_color rgb(" + colscm["[Colors:View]"]["ForegroundNormal"] + ");")
        # Misc.
        if darkmode:
            result.insert(41, "@define-color shade_color rgba(0, 0, 0, 0.36);")
        else:
            result.insert(42, "@define-color shade_color rgba(0, 0, 0, 0.09);")
        if darkmode:
            result.insert(41, "@define-color scrollbar_outline_color rgba(" + colscm["[Colors:View]"]["BackgroundNormal"] + ",0.5);")
        else:
            result.insert(42, "@define-color scrollbar_outline_color rgb(" + colscm["[Colors:View]"]["BackgroundNormal"] + ");")

        #Save changes to file
        with open(gtkcssfile, 'w') as fp:
            fp.write("\n".join(result))

dbouos()
loop = GLib.MainLoop()
loop.run()
