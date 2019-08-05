#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Path Handling for epic pipeline.
"""
#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# internal
from maya_utils import maya_tools_dir

#------------------------------------------------------------------------------#
#--------------------------------------------------------------------- PATHS --#

# root
maya_tools = maya_tools_dir()
general_dir = "{0}/General".format(maya_tools)
art_dir = "{0}/ART".format(general_dir)
scripts_dir = "{0}/Scripts".format(general_dir)

# epic
epic_dir = "{0}/epic".format(scripts_dir)
resources_dir = "{0}/resources".format(epic_dir)
stylesheets = "{0}/Stylesheets".format(resources_dir)
aaron_dark_stylesheet = "{0}/aaron_dark.qss".format(stylesheets)

# ART paths
skin_weights = "{0}/SkinWeights".format(art_dir)
joint_mover_templates = "{0}/JointMoverTemplates".format(art_dir)
skeleton_templates = "{0}/SkeletonTemplates".format(art_dir)


