#!/usr/bin/python
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    useful decorators to inhance code functionality.

"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# third party
from maya import cmds

#------------------------------------------------------------------------------#
#---------------------------------------------------------------- DECORATORS --#

def undo(func):
    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        try:
            ret = func(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
        return ret
    return wrapper
