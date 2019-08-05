#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    System Utilities.
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# built-in
import os
import sys
import json

# third-party
from maya import cmds

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

def json_save(data=None, path=None):
    """Saves out given data into a json file."""
    if not path:
        path = cmds.fileDialog2(fm=0, ds=2, ff="*.json", rf=True)
        if not path:
            return
        path = path[0]

    data = json.dumps(data, sort_keys=True, ensure_ascii=True, indent=2)
    fobj = open(path, 'w')
    fobj.write(data)
    fobj.close()

    return path

def json_load(path=None):
    """This procedure loads and returns the content of a json file."""
    if not path:
        path = cmds.fileDialog2(fm=1, ds=2, ff="*.json")
        if not path:
            return
        path = path[0]

    fobj = open(path)
    data = json.load(fobj)
    return data

def win_path_convert(path=None):
    """Converts \ to /"""
    separator = os.sep
    if separator != "/":
        path = path.replace(os.sep, "/")
    return path

def reset_all_modules():
    """Resets all system modules, used for reloading."""
    if globals().has_key('init_modules'):
        for m in [x for x in sys.modules.keys() if x not in init_modules]:
            del(sys.modules[m])
    else:
        init_modules = sys.modules.keys()
