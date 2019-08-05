#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Base class for UI constructors.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import shiboken

# external
from epic.utils import path_lib

# 3rd party
from maya import cmds, OpenMaya
import maya.OpenMayaUI as mui
from PySide import QtGui, QtCore
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- CLASSES --#

class MainWindow(QtGui.QMainWindow):
    def keyPressEvent(self, event):
        """Override keyPressEvent to keep focus on QWidget in Maya."""
        if (event.modifiers() & QtCore.Qt.ShiftModifier):
            self.shift = True
            pass # make silent

class UIUtils(MayaQWidgetBaseMixin, QtGui.QWidget):
    """Base class for UI constructors."""

    # globals
    save_button = QtGui.QMessageBox.Yes
    multiple_selection = QtGui.QAbstractItemView.ExtendedSelection

    def window(self, wname=None, wtitle=None, cwidget=None, on_top=None,
               styling=None):
        """Defines basic window parameters."""
        parent = self.get_maya_window()
        window = MainWindow(parent)

        self.window_name = wname

        if wname:
            window.setObjectName(wname)
        if wtitle:
            window.setWindowTitle(wtitle)
        if cwidget:
            window.setCentralWidget(cwidget)
        if on_top:
            self.set_on_top(window, on=True)
        if styling == "dark":
            style_sheet_file = QtCore.QFile(path_lib.aaron_dark_stylesheet)
            style_sheet_file.open(QtCore.QFile.ReadOnly)
            window.setStyleSheet(str(style_sheet_file.readAll()))

        return window

    def set_on_top(self, window, off=None, on=None):
        if off:
            args = [window.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint]
            window.setWindowFlags(*args)
            window.show()
            return
        if on:
            args = [window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint]
            window.setWindowFlags(*args)
            window.show()
            return

        # toggle
        args = [window.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint]
        window.setWindowFlags(*args)
        window.show()

    def get_maya_window(self):
        """Grabs the Maya window."""
        pointer = mui.MQtUtil.mainWindow()
        return shiboken.wrapInstance(long(pointer), QtGui.QWidget)

    def widget(self):
        """Main Widget"""
        return QtGui.QWidget()

    def qt_divider_label(self, layout, label):
        """Creates a centered label header."""
        # attach to layout
        divider_layout = QtGui.QHBoxLayout()
        layout.addLayout(divider_layout)

        # define divider
        divider_label = QtGui.QLabel(label)
        divider_label.setAlignment(QtCore.Qt.AlignCenter)
        divider_label.setMinimumHeight(20)
        divider_left = QtGui.QFrame()
        divider_left.setFrameShape(QtGui.QFrame.HLine)
        divider_left.setFrameShadow(QtGui.QFrame.Sunken)
        divider_right = QtGui.QFrame()
        divider_right.setFrameShape(QtGui.QFrame.HLine)
        divider_right.setFrameShadow(QtGui.QFrame.Sunken)
        divider_layout.addWidget(divider_left)
        divider_layout.addWidget(divider_label)
        divider_layout.addWidget(divider_right)

    def qt_list_widget_add_items(self, widget, items, clear=None, dup=None):
        """Qt Wrapper for QListWidget for adding items."""
        if clear:
            self.clear_widget(widget)
        for item_text in items:
            item = QtGui.QListWidgetItem(item_text)
            if dup:
                if widget.findItems(item.text(), QtCore.Qt.MatchExactly):
                    continue
            widget.addItem(item)

    def list_widget_find_all_items(self, widget):
        """Finds all items in a QListWidget"""
        all_items = list()
        for index in xrange(widget.count()):
            all_items.append(widget.item(index).text())
        return all_items

    def qt_list_widget_remove_items(self, widget):
        """Qt Wrapper for QListWidget for removing items"""
        for item in widget.selectedItems():
            widget.takeItem(widget.row(item))

    def clear_widget(self, widget):
        """Clears items in a widget."""
        widget.clear()

    def warning(self, message, button_one=None, button_two=None):
        """Method for prompting the user with a warning."""
        if not button_one:
            button_one = QtGui.QMessageBox.Ok
        if not button_two:
            button_two = QtGui.QMessageBox.Cancel
        args = [self, "Warning", message, button_one, button_two]
        warning = QtGui.QMessageBox.warning(*args)
        return warning

    def widget_state(self, widgets, state=None, exclude=None):
        """Enables/Disables Widgets based on their current state.
            @PARAMS:
                :widgets: list, widgets.
                :state: "disable", "enable", None = toggle
        """
        for widget in widgets:
            if exclude:
                if widget in exclude:
                    continue
            if state == "disable":
                widget.setEnabled(False)
            elif state == "enable":
                widget.setEnabled(True)
            else: # toggle
                if widget.isEnabled():
                    widget.setEnabled(False)
                elif not widget.isEnabled():
                    widget.setEnabled(True)

    def header_image(self, layout, path):
        """Creates header image."""
        label = QtGui.QLabel()
        pixmap = QtGui.QPixmap(path)
        label.setPixmap(pixmap)

        layout.addWidget(label)

    def keyPressEvent(self, event):
        """Override keyPressEvent to keep focus on QWidget in Maya."""
        QtGui.QMessageBox.information(self, "Key Press Detected!", "You Pressed: " + event.text())
        pass
        # if (event.modifiers() & QtCore.Qt.ShiftModifier):
            # self.shift = True
            # pass # make silent

    @classmethod
    def clear_settings(cls, settings, info=None):
        """Clears out the Epic Games Menu settings"""
        settings.clear()
        if not info:
            info = "Settings have been Reset."
        OpenMaya.MGlobal.displayWarning(info)

    @classmethod
    def get_open_filename(cls, cap, file_filter, start_path=None,
                          existing_dir=None):
        """File Dialog that returns selected path."""

        file_dialog = QtGui.QFileDialog()
        file_dialog.setLabelText(QtGui.QFileDialog.Accept, "Import")
        if existing_dir:
            args = [file_dialog, cap]
            return file_dialog.getExistingDirectory(*args)
        if not start_path:
            start_path = QtCore.QDir.currentPath()
        args = [file_dialog, cap, start_path, file_filter]
        return file_dialog.getOpenFileName(*args)


