#------------------------------------------------------------------------------#
#-------------------------------------------------------------------- HEADER --#

"""
:author:
    acarlisle

:description:
    Post Scripts
"""

#------------------------------------------------------------------------------#
#------------------------------------------------------------------- IMPORTS --#

# 3rd party
from maya import cmds

#------------------------------------------------------------------------------#
#----------------------------------------------------------------- FUNCTIONS --#

#------------------------------------------------------------------------------#
def create_polevector_follow(control, joint):
    """Creates a linear curve between a joint and a control."""
    # world space
    joint_world_space = cmds.xform(control, q=True, ws=True, rp=True)
    control_world_space = cmds.xform(joint, q=True, ws=True, rp=True)

    # create curve and clusters
    curve = cmds.curve(d=1, p=[joint_world_space, control_world_space], n="{0}_curve".format(control))
    cmds.setAttr("{0}.overrideEnabled".format(curve), 1)
    cmds.setAttr("{0}.overrideDisplayType".format(curve), 1)
    joint_cluster = cmds.cluster("{0}.cv[0]".format(curve), n="{0}_cluster".format(joint))
    control_cluster = cmds.cluster("{0}.cv[1]".format(curve), n="{0}_cluster".format(control))

    # set hierarchy
    groupNode = cmds.group(joint_cluster, control_cluster, curve, n=curve+"_grp")
    cmds.parent(groupNode, "rig_grp")
    cmds.parentConstraint(control, joint_cluster, mo=False)
    cmds.parentConstraint(joint, control_cluster, mo=False)

    # hide
    cmds.hide(joint_cluster)
    cmds.hide(control_cluster)

#------------------------------------------------------------------------------#
def hide_controls(controls):
    """Hides controls"""
    cmds.hide(controls)

#------------------------------------------------------------------------------#
def dynamics_off(dynamic_sets):
    """Turns off Dynamics for a list of objects."""
    for one in dynamic_sets:
        cmds.setAttr(one+".chainStartEnvelope", 0)
        cmds.setAttr(one+".chainStartEnvelope", l=True)

#------------------------------------------------------------------------------#
def add_capsule(radius=None, half_height=None):
    if not radius:
        radius = 42
    if not half_height:
        half_height = 86

    trueHalfHeight = (half_height*2)-(radius*2)
    capsule = cmds.polyCylinder(name="collision_capsule",
                                r=radius,
                                h=trueHalfHeight,
                                sx=18, sy=1, sz=5,
                                ax=[0,0,1], rcp=True, cuv=3, ch=True)
    cmds.setAttr(capsule[0]+".tz", half_height+2.2)
    cmds.setAttr(capsule[0]+".rz", 90)

    cmds.addAttr(capsule[0], ln="Radius", dv=radius, keyable=True)
    cmds.addAttr(capsule[0], ln="HalfHeight", dv=half_height, keyable=True)

    expr = str(capsule[1]+".radius = "+capsule[0]+".Radius;\n"+
               capsule[1]+".height = ("+capsule[0]+".HalfHeight*2) - ("+
               capsule[0]+".Radius*2);")
    cmds.expression(s=expr, o=capsule[1], ae=1, uc="all")

    cmds.setAttr(capsule[0]+".overrideEnabled", 1)
    cmds.setAttr(capsule[0]+".overrideColor", 18)
    cmds.setAttr(capsule[0]+".overrideShading", 0)

    cmds.addAttr(capsule[0], ln="Shaded", dv=0, min=0, max=1, keyable=True)
    cmds.connectAttr(capsule[0]+".Shaded", capsule[0]+".overrideShading")

    cmds.parentConstraint("root", capsule[0], mo=True)
    cmds.select(capsule[0], r=True)
    capsuleDisplayLayer = cmds.createDisplayLayer(nr=True,
                                                  name="Collision Capsule")
    cmds.setAttr(capsuleDisplayLayer+".displayType", 2)
    cmds.setAttr(capsuleDisplayLayer+".v", 0)

    for attr in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]:
        cmds.setAttr(capsule[0]+"."+attr, lock=True,
                     keyable=False, channelBox=False)
    cmds.select(clear=True)

#------------------------------------------------------------------------------#
def create_game_cam():
    """Adds a game cam to the scene."""
    game_cam = cmds.camera(centerOfInterest=5, focalLength=18,
                           lensSqueezeRatio=1, cameraScale=1,
                           horizontalFilmAperture=1.41732,
                           horizontalFilmOffset=0,
                           verticalFilmAperture=0.94488,
                           verticalFilmOffset=0, filmFit="Overscan",
                           overscan=1.05, motionBlur=0, shutterAngle=144,
                           nearClipPlane=1.0, farClipPlane=10000, orthographic=0,
                           orthographicWidth=30, panZoomEnabled=0,
                           horizontalPan=0, verticalPan=0, zoom=1,
                           displayFilmGate=True)[0]
    game_cam = cmds.rename(game_cam, "GameCam")
    cmds.camera(game_cam, e=True, horizontalFilmAperture=1.6724376,
                focalLength=21.2399857011)
    cmds.setAttr(game_cam+".displayGateMaskOpacity", 1)
    cmds.setAttr(game_cam+".displayGateMaskColor", 0, 0, 0, type="double3")
    cmds.setAttr(game_cam+".r", 90, 0, 180, type="double3")

    # Create the control
    control = cmds.circle(name=game_cam+"_Ctrl", ch=True, o=True, r=15)[0]
    cmds.makeIdentity(control, a=True, t=True, r=True, s=True)

    # Create groups for the sdk and the constraints
    const_grp = cmds.group(control, name=control+"_grp")
    if cmds.objExists("rig_grp"):
        cmds.parent(const_grp, "rig_grp")

    # Parent Constrain the cam to the control
    cmds.parentConstraint(control, game_cam, mo=True)
    cmds.connectAttr(control+".visibility", game_cam+".visibility", f=True)
    cmds.setAttr(const_grp+".v", 0)
    cmds.setAttr(const_grp+".t", 0, 500, 200, type="double3")

#------------------------------------------------------------------------------#
def add_ik_bones(weapon=None):
    if not weapon:
        weapon = "weapon_r"
        if not cmds.objExists("weapon_r"):
            weapon = "hand_r"
    try:
        # create the joints
        cmds.select(clear = True)
        ikFootRoot = cmds.joint(name = "ik_foot_root")
        cmds.select(clear = True)

        cmds.select(clear = True)
        ikFootLeft = cmds.joint(name = "ik_foot_l")
        cmds.select(clear = True)

        cmds.select(clear = True)
        ikFootRight = cmds.joint(name = "ik_foot_r")
        cmds.select(clear = True)

        cmds.select(clear = True)
        ikHandRoot = cmds.joint(name = "ik_hand_root")
        cmds.select(clear = True)

        cmds.select(clear = True)
        ikHandGun = cmds.joint(name = "ik_hand_gun")
        cmds.select(clear = True)

        cmds.select(clear = True)
        ikHandLeft = cmds.joint(name = "ik_hand_l")
        cmds.select(clear = True)

        cmds.select(clear = True)
        ikHandRight = cmds.joint(name = "ik_hand_r")
        cmds.select(clear = True)

        # create hierarhcy
        cmds.parent(ikFootRoot, "root")
        cmds.parent(ikHandRoot, "root")
        cmds.parent(ikFootLeft, ikFootRoot)
        cmds.parent(ikFootRight, ikFootRoot)
        cmds.parent(ikHandGun, ikHandRoot)
        cmds.parent(ikHandLeft, ikHandGun)
        cmds.parent(ikHandRight, ikHandGun)

        # constrain the joints
        rightHandGunConstraint = cmds.parentConstraint("spine_03", ikHandRoot)[0]
        rightHandGunConstraint = cmds.parentConstraint(weapon, ikHandGun)[0]
        leftHandConstraint = cmds.parentConstraint("hand_l", ikHandLeft)[0]
        rightHandConstraint = cmds.parentConstraint("hand_r", ikHandRight)[0]
        leftFootConstraint = cmds.parentConstraint("foot_l", ikFootLeft)[0]
        rightFootConstraint = cmds.parentConstraint("foot_r", ikFootRight)[0]
    except:
        cmds.warning("Something went wrong")

#------------------------------------------------------------------------------#
def assume_model_pose_jm():
        info = cmds.getAttr("Model_Pose.notes")
        poseInfo = info.splitlines()
        for pose in poseInfo:
            pose = pose.lstrip("[")
            pose = pose.rstrip("]")
            splitString = pose.split(",")
            mover = splitString[0].strip("'")
            tx = splitString[1]
            ty = splitString[2]
            tz = splitString[3]
            rx = splitString[4]
            ry = splitString[5]
            rz = splitString[6]
            sx = splitString[7]
            sy = splitString[8]
            sz = splitString[9]

            if cmds.getAttr(mover + ".tx", lock = True) == False:
                cmds.setAttr(mover + ".tx", float(tx))
            if cmds.getAttr(mover + ".ty", lock = True) == False:
                cmds.setAttr(mover + ".ty", float(ty))
            if cmds.getAttr(mover + ".tz", lock = True) == False:
                cmds.setAttr(mover + ".tz", float(tz))

            if cmds.getAttr(mover + ".rx", lock = True) == False:
                cmds.setAttr(mover + ".rx", float(rx))
            if cmds.getAttr(mover + ".ry", lock = True) == False:
                cmds.setAttr(mover + ".ry", float(ry))
            if cmds.getAttr(mover + ".rz", lock = True) == False:
                cmds.setAttr(mover + ".rz", float(rz))

            if cmds.getAttr(mover + ".sx", keyable = True) == True:
                cmds.setAttr(mover + ".sx", float(sx))
            if cmds.getAttr(mover + ".sy", keyable = True) == True:
                cmds.setAttr(mover + ".sy", float(sy))
            if cmds.getAttr(mover + ".sz", keyable = True) == True:
                cmds.setAttr(mover + ".sz", float(sz))

        #turn the vis on for the rig pose node to show we are in that mode
        if cmds.objExists("Rig_Pose"):
            cmds.setAttr("Rig_Pose.v", 0)
        cmds.setAttr("Model_Pose.v", 1)

#------------------------------------------------------------------------------#
def set_model_pose_skel():
        info = cmds.getAttr("Skeleton_Model_Pose.notes")
        poseInfo = info.splitlines()
        for pose in poseInfo:
            pose = pose.lstrip("[")
            pose = pose.rstrip("]")
            splitString = pose.split(",")
            mover = splitString[0].strip("'")
            tx = splitString[1]
            ty = splitString[2]
            tz = splitString[3]
            rx = splitString[4]
            ry = splitString[5]
            rz = splitString[6]


            if cmds.getAttr(mover + ".tx", lock = True) == False:
                cmds.setAttr(mover + ".tx", float(tx))
            if cmds.getAttr(mover + ".ty", lock = True) == False:
                cmds.setAttr(mover + ".ty", float(ty))
            if cmds.getAttr(mover + ".tz", lock = True) == False:
                cmds.setAttr(mover + ".tz", float(tz))

            if cmds.getAttr(mover + ".rx", lock = True) == False:
                cmds.setAttr(mover + ".rx", float(rx))
            if cmds.getAttr(mover + ".ry", lock = True) == False:
                cmds.setAttr(mover + ".ry", float(ry))
            if cmds.getAttr(mover + ".rz", lock = True) == False:
                cmds.setAttr(mover + ".rz", float(rz))


#------------------------------------------------------------------------------#
def add_custom_curves(curves=["DistanceCurve", "DistanceToApex"]):
    """Add distance curve to root joint for engine use."""
    joint_attrs = cmds.listAttr("root")
    attributes = curves
    for attribute in attributes:
        exists = False
        for joint_attribute in joint_attrs:
            if joint_attribute.find(attribute) != -1:
                exists = True
        if exists == False:
            cmds.addAttr("root", ln=attribute, keyable=True)

#------------------------------------------------------------------------------#
def open_export_file():
    """Opens export file."""
    # Save
    cmds.file(save = True, type = "mayaBinary", force = True)

    # Open Export File
    scene_name = cmds.file(q = True, sceneName = True).split("AnimRigs")
    project = "{0}ExportFiles".format(scene_name[0])
    export_file = "{0}{1}_Export.mb".format(project, scene_name[1].split(".")[0])
    cmds.file(export_file, open=True, force=True)
