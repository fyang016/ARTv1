#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Maya utilities.
"""
#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import sys
import os

# third-party
import maya.api.OpenMaya as OpenMaya
from maya import cmds

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

def find_all_incoming(start_nodes, max_depth=None):
    """
    Recursively finds all unique incoming dependencies for the specified node.
    """
    dependencies = set()
    _find_all_incoming(start_nodes, dependencies, max_depth, 0)
    return list(dependencies)

def _find_all_incoming(start_nodes, dependencies, max_depth, depth):
    """
    Recursively finds all unique incoming dependencies for the specified node.
    """
    if max_depth and depth > max_depth:
        return
    kwargs = dict(s=True, d=False)
    incoming = cmds.listConnections(list(start_nodes), **kwargs)
    if not incoming:
        return
    non_visitied = set(cmds.ls(incoming, l=True)).difference(dependencies)
    dependencies.update(non_visitied)
    if non_visitied:
        _find_all_incoming(non_visitied, dependencies, max_depth, depth + 1)

def find_all_outgoing(start_nodes, max_depth=None):
    """
    Recursively finds all unique outgoing dependents for the specified node.
    """
    dependents = set()
    _find_all_outgoing(start_nodes, dependents, max_depth, 0)
    return list(dependents)

def _find_all_outgoing(start_nodes, dependents, max_depth, depth):
    """
    Recursively finds all unique outgoing dependents for the specified node.
    """
    if max_depth and depth > max_depth:
        return
    kwargs = dict(s=True, d=False)
    outgoing = cmds.listConnections(list(start_nodes), **kwargs)
    if not outgoing:
        return
    non_visitied = set(cmds.ls(outgoing, l=True)).difference(dependents)
    dependents.update(non_visitied)
    if non_visitied:
        _find_all_outgoing(non_visitied, dependents, max_depth, depth + 1)

def find_top_parent(dag_object):
    """Finds the top parent of a dag object
        @PARAMS:
            dag_object: string
    """
    if not cmds.objExists(dag_object):
        return cmds.warning("Object '{0}' does not exist.".format(dag_object))
    dag_path = cmds.ls(dag_object, l=True)[0]
    return dag_path.split("|")[1]

def maya_tools_dir():
    """Returns users mayaToolDir path"""
    tools_path = cmds.internalVar(usd = True) + "mayaTools.txt"
    if os.path.exists(tools_path):
        f = open(tools_path, 'r')
        tools_path = f.readline()
        f.close()
        return tools_path

def select_geometry():
    """Selects all geometry in the scene."""
    relatives = cmds.listRelatives(cmds.ls(geometry=True), p=True, path=True)
    cmds.select(relatives, r=True)

def unused_materials(delete=None, material_type=None):
    """Deletes unused materials.
        @PARAMS:
            delete: boolean, True deletes materials.
            material_type: string, "phong".
        :NOTE: Delete unused Nodes in Maya seems to fail for some reason.
        Also, instead of wrapping try/except in here, wrap this function in
        a try/except using the epic logger.
    """
    # globals
    deleted_materials = list()
    ignore_materials = ["lambert1", "particleCloud1"]

    # find materials
    materials = cmds.ls(type=material_type)
    if not material_type:
        materials = cmds.ls(mat=True)

    # remove unused materials
    for material in materials:
        if material in ignore_materials:
            continue
        cmds.hyperShade(objects=material)
        assigned_geo = cmds.ls(sl=True)
        if not assigned_geo:
            if delete:
                cmds.delete(material)
            deleted_materials.append(material)
    return deleted_materials

def reorder_outliner(objects=None):
    """Reorders the outliner based of selection.
        @PARAMS:
            objects: list, list of dag objects.
    """
    selection = cmds.ls(sl=True)
    if objects:
        selection = objects
    selection = sorted(selection, key=lambda s: s.lower())
    for dag_obj in selection:
        cmds.reorder(dag_obj, b=True)

def create_menu_item(label, parent, sub_menu, tear_off, divider):
    """Maya wrapper for creating menu items."""
    menu = cmds.menuItem(label, parent=parent, label=label,
                  subMenu=sub_menu, to=tear_off, divider=divider)
    return menu

def edit_menu_item(label, command):
    """Maya wrapper for adding commands to a menu."""
    label = label.replace(" ", "_")
    cmds.menuItem(label, e=True, command=command)
