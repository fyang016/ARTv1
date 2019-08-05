#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Epic Menu Constructor
"""
#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import re
import os
import sys
import imp

# third-party
from functools import partial
from maya import cmds, mel, OpenMaya, OpenMayaMPx

# external
from epic.utils.system_utils import win_path_convert, json_load, json_save

# deprication
try:
    from PySide import QtGui, QtCore
    from epic.utils.ui_utils import UIUtils
except:
    UIUtils = object

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- GLOBALS --#

ROOT = os.path.split(__file__)[0]
INCLUDE = ["Animation", "Rigging", "Utils", "aA.R.T.1.0", "aA.R.T.2.0"]
PROJECTS = ["zFortnite", "zParagon"]
IGNORE = list()
MENU_PATHS = dict()
PARENT = mel.eval('$temp1 = $gMainWindow')
MENU_FLAGS = ["NICENAME", "ANNOTATION", "BOLD", "ENABLE"]

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

def _reload(ignore):
    import epic_menu
    reload(epic_menu)
    menu = epic_menu.EpicMenu(ignore)
    menu._remove_menus()
    menu.create_menus()

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#


class EpicMenu(UIUtils):
    def __init__(self,ignore=None, *args, **kwargs):

        # settings
        self.settings_path = "{0}/menu_settings.json".format(ROOT)
        self.settings = dict()
        if os.path.exists(self.settings_path):
            self.settings = json_load(self.settings_path)

        # for additional setting checks (perforce)
        if ignore:
            IGNORE.append(ignore)

        # globals
        self.menu_paths = dict()
        self.checkboxes = dict()

    def create_menus(self):
        for directory in os.listdir(ROOT):
            # check settings
            path = "{0}/{1}".format(ROOT, directory)
            if (directory in INCLUDE or directory in PROJECTS):
                label = "e{0}".format(directory)
                # for alphabatizing
                if directory.startswith("aA.R.T.") or directory in PROJECTS:
                    label = directory.split(directory[0])[-1]
                name = self._menu_name_check(label)
                MENU_PATHS[name] = path
                if self._settings():
                    if not self._settings(name):
                        IGNORE.append(name)
                        continue
                cmds.menu(name, parent=PARENT, label=label, to=True)
        if MENU_PATHS:
            self._create_sub_menus(MENU_PATHS, IGNORE)

    def _menu_name_check(self, label):
        """Returns a useable menu label/name."""
        name = label.replace(" ", "_")
        if "." in name:
            name = name.replace(".", "_")
        return name

    def remove_menus(self, menu_build=None, *args):
        """Remove's Specific Menus."""
        menus = cmds.window(PARENT, q=True, menuArray=True)
        if menu_build:
            for menu, path in menu_build.items():
                if menu not in menus:
                    label = menu
                    cmds.menu(menu, parent=PARENT, label=label, to=True)
                    if label in IGNORE:
                        IGNORE.remove(label)
                    return self._create_sub_menus(menu_build, IGNORE)
                return cmds.deleteUI(menu)
        EpicMenu._remove_menus()

    def _create_sub_menus(self, menu_paths, ignore=None):
        """Recursively create's submenu's off dictionary, my god this is ugly.
            @PARAMS:
                :menu_paths: dict, {"menu_name" : "path"}
                :ignore: list
        """
        paths = dict()
        menu_path = None
        # iterate
        for menu, path in menu_paths.items():
            if ignore and menu in ignore:
                continue
            for sub_menu in os.listdir(path):
                sub_path = "{0}/{1}".format(path, sub_menu)
                if os.path.isdir(sub_path):
                    uid = os.path.dirname(sub_path).split("/")[-1]
                    label = os.path.basename(sub_path)
                    if ignore and label in ignore:
                        continue
                    menu_path = self._create_menu_item(label, menu, True,
                                                       True, False, uid)
                    additionals = os.listdir(sub_path)
                    if additionals and menu_path:
                        for level in additionals:
                            if os.path.isdir(sub_path):
                                paths[menu_path] = sub_path
                            elif os.path.isfile(sub_path):
                                label = os.path.basename(sub_path).split(".")[0]
                                if ignore and label in ignore:
                                    continue
                                self._build_menu_item(sub_path, label, menu)
                elif os.path.isfile(sub_path):
                    label = os.path.basename(sub_path).split(".")[0]
                    if ignore and label in ignore:
                        continue
                    self._build_menu_item(sub_path, label, menu)
        # continue
        if paths:
            self._create_sub_menus(paths)

    def _build_menu_item(self, path, label, menu):
        """Builds Menu Item command, label and uid"""
        annotation = None
        bold = False
        enable = True
        uid = os.path.dirname(path).split("/")[-1]
        command = self._find_run_it(label, path)
        menu_flags = self._find_run_it(label, path, True)
        if menu_flags:
            if "NICENAME" in menu_flags:
                label = menu_flags["NICENAME"]
            if "ANNOTATION" in menu_flags:
                annotation = menu_flags["ANNOTATION"]
            if "BOLD" in menu_flags:
                bold = menu_flags["BOLD"]
                if not isinstance(bold, bool):
                    bold = False
            if "ENABLE" in menu_flags:
                enable = menu_flags["ENABLE"]
                if not isinstance(enable, bool):
                    enable = True
        if command:
            try:
                self._create_menu_item(label, menu, False, True,
                                       False, uid, annotation, bold, enable)
                self._edit_menu_item(label, command, uid, bold)
            except Exception, e:
                pass

    def _create_menu_item(self, label, parent, sub_menu, tear_off, divider,
                          uid, annotation=None, bold=False, enable=True):
        """Maya wrapper for creating menu items."""
        menu_name = self._menu_name_check(label + uid)
        parent = self._menu_name_check(parent)
        if not enable:
            divider = True
        # TODO: get bold working
        return cmds.menuItem(menu_name, parent=parent, label=label,
                             ann=annotation, subMenu=sub_menu, to=tear_off,
                             divider=divider, enable=enable)

    def _edit_menu_item(self, label, command, uid, bold=False):
        """Maya wrapper for adding commands to a menu."""
        menu_name = self._menu_name_check(label + uid)
        cmds.menuItem(menu_name, e=True, command=command, bld=bold)

    def _find_run_it(self, label, path, menu_flags=None):
        """Find's the modules inside of a given class."""
        if not path.endswith(".py"):
            return
        path = win_path_convert(path)
        dir_path = win_path_convert(os.path.dirname(path))
        flags = dict()
        try:
            if menu_flags:
                for flag in MENU_FLAGS:
                    try:
                        run_it = imp.load_source(label, path)
                        exec("value = run_it.{0}".format(flag))
                        flags[flag] = value
                    except Exception:
                        continue
                return flags
            command = "import imp\n"
            command += "run_it = imp.load_source('{0}', '{1}')\n".format(label,
                                                                         path)
            command += "run_it.__run_it__()"
            return command
        except Exception:
            return

    def menu_manager(self):
        """For managing Menus (turning on, off)."""
        window_name = "epic_menu_manager"
        window_title = "Epic Menu Manager"
        widget = self.widget()

        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name, window=True)

        window = self.window(window_name, window_title, widget)
        window.setMinimumWidth(500)
        layout = QtGui.QVBoxLayout(widget)

        # turn on/off menus
        menu_build = dict()
        for menu, path in MENU_PATHS.items():
            if menu == "eUtils":
                continue
            menu_layout = QtGui.QHBoxLayout()
            layout.addLayout(menu_layout)

            # checkboxes
            self.checkboxes[menu] = QtGui.QCheckBox(menu)
            self.checkboxes[menu].setMinimumWidth(100)
            self.checkboxes[menu].setChecked(True)
            if self._settings():
                for key in self._settings().keys():
                    if key == menu:
                        checked = self._settings(menu)
                        self.checkboxes[menu].setChecked(checked)

            # paths
            line_edit = QtGui.QLineEdit()
            line_edit.setText(path)

            # layout
            menu_layout.addWidget(self.checkboxes[menu])
            menu_layout.addWidget(line_edit)

            # signals
            menu_build[menu] = path
            self.checkboxes[menu].stateChanged.connect(partial(self.remove_menus, menu_build))
            self.checkboxes[menu].stateChanged.connect(partial(self._save, self.checkboxes))
            self.checkboxes[menu].stateChanged.connect(EpicMenu.epic_reload)
            menu_build = dict()

        window.show()

    def _save(self, widgets, *args):
        """Saves settings for the menu_manager.
            @PARAMS:
                widgets: dict, "menu" : widget.
        """
        if widgets:
            for menu, widget in widgets.items():
                self.settings[menu] = widget.isChecked()
                json_save(self.settings, self.settings_path)

    def _settings(self, menu=None):
        """Returns QSettings and boolean values, instead of unicode.
            @PARAMS:
                menu: str, returns the value of the key menu.
        """
        settings = dict()
        if self.settings.keys():
            for key, value in self.settings.iteritems():
                if value == "true":
                    value = True
                elif value == "false":
                    value = False
                settings[key] = value
                if menu:
                    if menu == key:
                        return value
        return settings

    @classmethod
    def _remove_menus(cls):
        """Delete menus."""
        menus = cmds.window(PARENT, q=True, menuArray=True)
        for menu in MENU_PATHS.keys():
            if menu not in menus:
                continue
            cmds.deleteUI(menu)

    @classmethod
    def epic_reload(cls, ignore=None):
        """Handle's all reloading, dependency related."""
        # try:
        EpicMenu._remove_menus()
        _reload(ignore)
        return OpenMaya.MGlobal.displayInfo("Epic Menu Reloaded")

#------------------------------------------------------------------------------#
#---------------------------------------------------------- PLUGIN FUNCTIONS --#

def initializePlugin(mobject):
    menu = EpicMenu()
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Epic Menu, Inc.", "1.0")
    status = mplugin.registerUI(menu.create_menus, menu.remove_menus)
    return status

def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
