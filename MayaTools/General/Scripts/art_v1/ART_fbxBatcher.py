import maya.cmds as cmds
from functools import partial
import os, cPickle, math
import maya.mel as mel
import maya.utils
import sys
import time

# external
from epic.internal import epic_logger

class FBX_Batcher():

    def __init__(self):

        # logging
        self.logger = epic_logger.EpicLogger()
        self.logger.terminal(on_top=True) # terminal
        self.start = time.time()

        #get access to our maya tools
        toolsPath = cmds.internalVar(usd = True) + "mayaTools.txt"
        if os.path.exists(toolsPath):

            f = open(toolsPath, 'r')
            self.mayaToolsDir = f.readline()
            f.close()

        self.widgets = {}

        if cmds.window("ART_RetargetTool_UI", exists = True):
            cmds.deleteUI("ART_RetargetTool_UI")

        self.widgets["window"] = cmds.window("ART_RetargetTool_UI", title = "ART FBX Export Batcher", w = 400, h = 500, sizeable = False, mnb = False, mxb = False)

        #main layout
        self.widgets["layout"] = cmds.formLayout(w = 400, h = 500)

        #textField and browse button
        label = cmds.text(label = "Directory to Batch:")

        self.widgets["textField"] = cmds.textField(w = 300, text = "")
        self.widgets["browse"] = cmds.button(w = 70, label = "Browse", c = self.browse)

        self.widgets["optionalPathCB"] = cmds.checkBox(l="Optional Batch Export Path", ann="Check this if you want to export all of your files to a single location defined in the text field below.")
        self.widgets["ExportPathtextField"] = cmds.textField(w = 300, text = "", ann="Where do you want to export your files to?  This is optional and only used if the checkbox above is on")
        self.widgets["ExportPathbrowse"] = cmds.button(w = 70, label = "Browse", c = self.ExportPathbrowse)

        cmds.formLayout(self.widgets["layout"], edit = True, af = [(label, "left", 10),(label, "top", 10)])
        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["textField"], "left", 10),(self.widgets["textField"], "top", 30)])
        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["browse"], "right", 10),(self.widgets["browse"], "top", 30)])

        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["optionalPathCB"], "left", 10),(self.widgets["optionalPathCB"], "top", 60)])
        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["ExportPathtextField"], "left", 10),(self.widgets["ExportPathtextField"], "top", 80)])
        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["ExportPathbrowse"], "right", 10),(self.widgets["ExportPathbrowse"], "top", 80)])

        # CUSTOM FILE SCRIPT
        self.widgets["frame"] = cmds.frameLayout(w = 380, h = 100, bs = "etchedIn", cll = False, label = "Advanced", parent = self.widgets["layout"])
        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["frame"], "right", 10),(self.widgets["frame"], "top", 110)])
        self.widgets["advancedForm"] = cmds.formLayout(w = 380, h = 100, parent = self.widgets["frame"])

        label2 = cmds.text("Custom File Script:", parent =self.widgets["advancedForm"])
        self.widgets["scriptField"] = cmds.textField(w = 280, text = "", parent =self.widgets["advancedForm"])
        self.widgets["scriptBrowse"] = cmds.button(w = 70, label = "Browse", c = self.scriptBrowse, parent =self.widgets["advancedForm"])

        cmds.formLayout(self.widgets["advancedForm"], edit = True, af = [(label2, "left", 10),(label2, "top", 10)])
        cmds.formLayout(self.widgets["advancedForm"], edit = True, af = [(self.widgets["scriptField"], "left", 10),(self.widgets["scriptField"], "top", 30)])
        cmds.formLayout(self.widgets["advancedForm"], edit = True, af = [(self.widgets["scriptBrowse"], "right", 10),(self.widgets["scriptBrowse"], "top", 30)])

        # EXPORT AN FBX
        self.widgets["exportFBXCB"] = cmds.checkBox(label = "Export an FBX?", v = True, parent = self.widgets["layout"])
        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["exportFBXCB"], "left", 16),(self.widgets["exportFBXCB"], "top", 200)])

        # USE ANIM SEQ INFO
        self.widgets["useSequenceInfo"] = cmds.checkBox(label = "Use Anim Sequence Info?", v = True, parent = self.widgets["layout"])
        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["useSequenceInfo"], "left", 16),(self.widgets["useSequenceInfo"], "top", 220)])

        # EXPORT MORPHS
        self.widgets["exportMorphs"] = cmds.checkBox(label = "Export Morphs?", v = True, parent = self.widgets["layout"])
        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["exportMorphs"], "left", 16),(self.widgets["exportMorphs"], "top", 240)])

        # REMOVE ROOT ANIM
        self.widgets["removeRoot"] = cmds.checkBox(label = "Remove root animation?", v = False, parent = self.widgets["layout"])
        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["removeRoot"], "left", 16),(self.widgets["removeRoot"], "top", 260)])

        # DISABLE REDRAW
        self.widgets["disableRedraw"] = cmds.checkBox(label="Disable 3D viewport redraw", v=True, parent=self.widgets["layout"])
        cmds.formLayout(self.widgets["layout"], edit=True, af=[(self.widgets["disableRedraw"], "left", 16), (self.widgets["disableRedraw"], "top", 280)])

        #process button
        self.widgets["process"] = cmds.button(w = 380, h = 50, label = "BEGIN BATCH", c = self.process, parent = self.widgets["layout"])
        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["process"], "left", 10),(self.widgets["process"], "top", 330)])
        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["process"], "left", 10),(self.widgets["process"], "bottom", 360)])

        #progress bar
        text = cmds.text(label = "File Progress: ", parent = self.widgets["layout"])
        self.widgets["currentFileProgressBar"] = cmds.progressBar(w = 250, parent = self.widgets["layout"])

        cmds.formLayout(self.widgets["layout"], edit = True, af = [(text, "left", 10),(text, "top", 390)])
        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["currentFileProgressBar"], "left", 110),(self.widgets["currentFileProgressBar"], "top", 390)])

        text2 = cmds.text(label = "Total Progress: ", parent = self.widgets["layout"])
        self.widgets["progressBar"] = cmds.progressBar(w = 250, parent = self.widgets["layout"])

        cmds.formLayout(self.widgets["layout"], edit = True, af = [(text2, "left", 10),(text2, "top", 420)])
        cmds.formLayout(self.widgets["layout"], edit = True, af = [(self.widgets["progressBar"], "left", 110),(self.widgets["progressBar"], "top", 420)])

        #show window
        cmds.showWindow(self.widgets["window"])


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def browse(self, *args):
        try:
            directory = cmds.fileDialog2(dialogStyle=2, fm = 3)[0]
            cmds.textField(self.widgets["textField"], edit = True, text = directory)

        except:
            pass

    def ExportPathbrowse(self, *args):
        try:
            directory = cmds.fileDialog2(dialogStyle=2, fm = 3)[0]
            cmds.textField(self.widgets["ExportPathtextField"], edit = True, text = directory)
        except:
            pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def scriptBrowse(self, *args):
        try:
            directory = cmds.fileDialog2(dialogStyle=2, fm = 1)[0]
            cmds.textField(self.widgets["scriptField"], edit = True, text = directory)

        except:
            pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def dupeAndBake(self, step, character, startFrame, endFrame, exportAttrs = False, attrsToExport = None, *args):
        #sys.__stdout__.write("    duplicate the skeleton" + "\n")

        cmds.progressBar(self.widgets["currentFileProgressBar"], edit = True, step = step)
        dupeSkeleton = cmds.duplicate(character + ":" + "root", un = False, ic = False)
        cmds.select(dupeSkeleton[0], hi = True)
        cmds.delete(constraints = True)
        newSelection = cmds.ls(sl = True)
        newSkeleton = []
        for each in newSelection:
            newSkeleton.append(each)
        joints = []
        for each in newSkeleton:
            if cmds.nodeType(each) != "joint":
                cmds.delete(each)
            else:
                joints.append(each)

        #constrain the dupe skeleton to the original skeleton
        constraints = []
        #sys.__stdout__.write("    constrain dupe skeleton to original" + "\n")
        for joint in joints:
            #do some checks to make sure that this is valid
            parent = cmds.listRelatives(joint, parent = True)

            if parent != None:
                if parent[0] in joints:
                    constraint = cmds.parentConstraint(character + ":" + parent[0] + "|" + character + ":" + joint, joint)[0]
                    constraints.append(constraint)

            else:
                #root bone?
                if joint == "root":
                    constraint = cmds.parentConstraint(character + ":" + joint, joint)[0]
                    constraints.append(constraint)

                    if exportAttrs == True:

                        #sys.__stdout__.write("    exporting custom attr curves" + "\n")
                        constraint = cmds.parentConstraint(character + ":" + joint, joint)[0]
                        constraints.append(constraint)

                        #remove all custom attrs
                        allAttrs = cmds.listAttr("root", keyable = True)
                        normalAttrs = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ", "visibility"]

                        for attr in allAttrs:
                            if attr not in normalAttrs:
                                if cmds.objExists("root." + attr):
                                    cmds.deleteAttr("root", at = attr)


                        for attr in attrsToExport:
                            if cmds.objExists(character + ":root." + attr):
                                #sys.__stdout__.write("    exporting attr curve : " + str(attr) + "\n")
                                if not cmds.objExists("root." + attr):
                                    cmds.addAttr("root", ln = attr, keyable = True)

                                #disabling redraw
                                try:
                                    if cmds.checkBox(self.widgets["disableRedraw"], q=True, v=True) == True:
                                        mel.eval("paneLayout -e -manage false $gMainPane")
                                    for i in range(startFrame, endFrame + 1):
                                        cmds.currentTime(i)
                                        value = cmds.getAttr(character + ":root." + attr)
                                        cmds.setAttr("root." + attr, value)
                                        cmds.setKeyframe("root." + attr, itt = "linear", ott = "linear")
                                except Exception, e:
                                    logger.error(e, title='Crash in bake root attrs')
                                finally:
                                    mel.eval("paneLayout -e -manage true $gMainPane")

                                cmds.refresh(force = True)
                                cmds.selectKey("root." + attr)
                                cmds.keyTangent(itt = "linear", ott = "linear")

                    if exportAttrs == False:
                        allAttrs = cmds.listAttr("root", keyable = True)
                        normalAttrs = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ", "visibility"]

                        for attr in allAttrs:
                            if attr not in normalAttrs:
                                if cmds.objExists("root." + attr):
                                    cmds.deleteAttr("root", at = attr)


        #bake the animation down onto the export skeleton
        #sys.__stdout__.write("    bake animation" + "\n")
        cmds.progressBar(self.widgets["currentFileProgressBar"], edit = True, step = step)
        cmds.select("root", hi = True)

        #disabling redraw
        try:
            if cmds.checkBox(self.widgets["disableRedraw"], q=True, v=True) == True:
                mel.eval("paneLayout -e -manage false $gMainPane")
            cmds.bakeResults(simulation = True, t = (startFrame, endFrame))
        except Exception, e:
            logger.error(e, title='Crash in bakeResults')
        finally:
            mel.eval("paneLayout -e -manage true $gMainPane")
        cmds.delete(constraints)

        #run an euler filter
        cmds.select("root", hi = True)
        cmds.filterCurve()


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def getBlendshapes(self, step, character, startFrame, endFrame, *args):
        #get blendshapes
        allBlends = cmds.ls(type = "blendShape")
        jmBlends = ["calf_l_shapes",  "calf_r_shapes",  "head_shapes",  "l_elbow_shapes",  "r_elbow_shapes",  "l_lowerarm_shapes",  "r_lowerarm_shapes",  "l_shoulder_shapes",  "r_shoulder_shapes",  "l_upperarm_shapes",  "r_upperarm_shapes",
                    "neck1_shapes",  "neck2_shapes",  "neck3_shapes",  "pelvis_shapes",  "spine1_shapes",  "spine2_shapes",  "spine3_shapes",  "spine4_shapes",  "spine5_shapes",  "thigh_l_shapes",  "thigh_r_shapes"]
        blendshapes = []
        morphList = []

        if allBlends != None:
            for shape in allBlends:
                if shape.split(":")[-1] not in jmBlends:
                    if shape.split(":")[0] == character:
                        blendshapes.append(shape)

        #if our character has blendshapes, deal with those now
        cmds.progressBar(self.widgets["currentFileProgressBar"], edit = True, step = step)
        value = cmds.checkBox(self.widgets["exportMorphs"], q = True, v = True)
        if value:
            if blendshapes != None:
                if cmds.objExists("custom_export"):
                    cmds.delete("custom_export")

                cube = cmds.polyCube(name = "custom_export")[0]
                i = 1
                if blendshapes != None:
                    for shape in blendshapes:
                        attrs = cmds.listAttr(shape, m = True, string = "weight")
                        for attr in attrs:
                            morph = cmds.polyCube(name = attr)[0]
                            morphList.append(morph)
                            sys.__stdout__.write("Blendshape:" + morph + "\n")

                cmds.select(morphList, r = True)
                cmds.select(cube, add=True)
                cmds.blendShape(name = "custom_export_shapes")
                cmds.select(clear = True)

                cmds.delete(morphList)

            if blendshapes != None:
                #transfer keys from original to new morph

                #disabling redraw
                try:
                    if cmds.checkBox(self.widgets["disableRedraw"], q=True, v=True) == True:
                        mel.eval("paneLayout -e -manage false $gMainPane")
                    for x in range(startFrame, endFrame + 1):
                        for shape in blendshapes:
                            attrs = cmds.listAttr(shape, m = True, string = "weight")
                            #counter for index

                            for attr in attrs:

                                cmds.currentTime(x)
                                value = cmds.getAttr(shape + "." + attr)
                                cmds.setKeyframe("custom_export_shapes." + attr, t = (x), v = value)
                except Exception, e:
                    logger.error(e, title='Crash in blendshape bake loop')
                finally:
                    mel.eval("paneLayout -e -manage true $gMainPane")

        return blendshapes

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def getCharacters(self):
        referenceNodes = []
        references = cmds.ls(type = "reference")

        for reference in references:
            niceName = reference.rpartition("RN")[0]
            suffix = reference.rpartition("RN")[2]
            if suffix != "":
                if cmds.objExists(niceName + suffix + ":" + "Skeleton_Settings"):
                    referenceNodes.append(niceName + suffix)

            else:
                if cmds.objExists(niceName + ":" + "Skeleton_Settings"):
                    referenceNodes.append(niceName)

        return referenceNodes

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def process(self, *args):
        sys.__stdout__.write("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        self._duplicates = list()
        self._fbx_overwrites = list()
        self._errors = list()
        self._duplicates = list()
        self._fbx_files = list()
        self._maya_files = list()

        #new file
        cmds.file(new = True, force = True)

        #get the files in the directory
        directory = cmds.textField(self.widgets["textField"], q = True, text = True)
        filesInDir = os.listdir(directory)
        mayaFiles = []

        # grab full maya paths
        for file_name in filesInDir:
            full_path = "{0}/{1}".format(directory, file_name)
            if full_path.endswith(".mb") or full_path.endswith(".ma"):
                self._maya_files.append(full_path)

        for each in filesInDir:
            if each.rpartition(".")[2] == "mb":
                mayaFiles.append(each)

            ma_ = each.rpartition(".")[2] == "ma"
            if ma_:
                mayaFiles.append(each)

        #go through loop
        if len(mayaFiles) > 0:

            #get number of maya files
            numFiles = len(mayaFiles)
            amount = 100/ (numFiles + 1)
            newAmount = 0

            for mayaFile in mayaFiles:
                self.logger.info('<p style="background-color: #151515; height: 2px"> -- </p>', title=None)
                self.logger.info("", title="<b><font size=\"4\">EXPORT FILE: " + mayaFile + '</b></font>')
                sys.__stdout__.write("\n\n\nBeginning Export for: " + mayaFile + "\n")
                cmds.progressBar(self.widgets["progressBar"], edit = True, progress = newAmount + amount)

                #get name
                fileName = mayaFile.rpartition(".")[0]

                #open file
                directory = os.path.normpath(directory)
                cmds.file(os.path.join(directory, mayaFile), open = True, force = True, iv=True)

                #update
                cmds.progressBar(self.widgets["currentFileProgressBar"], edit = True, progress = 10)

                #execute custom script if it exists
                cmds.progressBar(self.widgets["currentFileProgressBar"], edit = True, progress = 20)
                script = cmds.textField(self.widgets["scriptField"], q = True, text = True)
                if script != "":
                    try:
                        sourceType = ""

                        if script.find(".py") != -1:
                            sourceType = "python"

                        if script.find(".mel") != -1:
                            sourceType = "mel"

                        #execute script
                        if sourceType == "mel":
                            command = ""
                            #open the file, and for each line in the file, add it to our command string.
                            f = open(script, 'r')
                            lines = f.readlines()

                            for line in lines:
                                command += line

                            import maya.mel as mel
                            mel.eval(command)

                        if sourceType == "python":
                            execfile("" + script + "")
                        sys.__stdout__.write("Custom Script succeeded: " + script + "\n")

                    except Exception, e:
                        self.logger.error(e, True, title=None)
                        self._errors.append(e)
                        #sys.__stdout__.write("ERROR: Custom Script failed for: " + mayaFile + "\n")
                        #sys.__stdout__.write("    Script Name: " + script + "\n")

                #export FBX
                #fbxPath = os.path.join(directory, "FBX")

                #get current frame range
                cmds.progressBar(self.widgets["currentFileProgressBar"], edit = True, progress = 30)
                start = cmds.playbackOptions(q = True, min = True)
                end = cmds.playbackOptions(q = True, max = True)
                doIExportFBX = cmds.checkBox(self.widgets["exportFBXCB"], q = True, v = True)

                if doIExportFBX:
                    try:
                        self.prepareForExportFBX(os.path.join(directory, fileName + ".fbx"), start, end)
                    except Exception, e:
                        self.logger.error(e, True, title=None)
                        self._errors.append(e)
                        # sys.__stdout__.write("ERROR: Could not export the fbx: " + fileName + ".fbx" + "\n\n")

                cmds.progressBar(self.widgets["currentFileProgressBar"], edit = True, progress = 40)

                #increment new amount
                newAmount = newAmount + amount

            # logging info
            self.logger.info('<p style="background-color: #151515; height: 2px"> -- </p>', title=None)
            self.logger.summary_header()

            #time duration result
            elapsed = (time.time() - self.start)
            timeText = 'PROCESS COMPLETED IN %.2f SECONDS.' % elapsed
            self.logger.info(timeText, title=None)

            self.logger.error(self._duplicates, title="DUPLICATES!!!", pretty=True)
            self.logger.error(self._errors, exc_info=True, title="SCRIPTS ERRORS", pretty=True)
            self.logger.warning(self._fbx_overwrites, title="FBX OVERWRITES", pretty=True)
            self.logger.info(self._fbx_files, title="FBX FILES", pretty=True)
            self.logger.info(self._maya_files, title="MAYA FILES", pretty=True)

        #new scene
        cmds.file(new = True, force = True)
        cmds.progressBar(self.widgets["progressBar"], edit = True, progress = 100)

        #delete UI
        cmds.deleteUI(self.widgets["window"])

        #confirm message
        cmds.confirmDialog(title = "Complete!", message = "Operation is complete!")


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def prepareForExportFBX(self, path, startFrame, endFrame, *args):
        sys.__stdout__.write("Preparing the File...\n")

        #get the characters in the scene
        characters = self.getCharacters()

        #get rotation interp
        options = cmds.optionVar(list = True)
        for op in options:
            if op == "rotationInterpolationDefault":
                interp = cmds.optionVar(q = op)
        cmds.optionVar(iv = ("rotationInterpolationDefault", 3))

        #Loop through each character in the scene, and export the fbx for that character
        cmds.progressBar(self.widgets["currentFileProgressBar"], edit = True, progress = 40)

        #create increment ammount for progress bar
        increment = 50/len(characters)
        step = increment/5


        #NEW: If use anim sequence info, get that info now
        if cmds.checkBox(self.widgets["useSequenceInfo"], q = True, v = True) == True:
            if cmds.objExists("ExportAnimationSettings"):
                sys.__stdout__.write("Using file anim sequence data" + "\n")
                sequeneces = cmds.listAttr("ExportAnimationSettings", string = "sequence*")

                for seq in sequeneces:
                    #get data
                    data = cmds.getAttr("ExportAnimationSettings." + seq)
                    dataList = data.split("::")
                    name = dataList[0]
                    start = dataList[1]
                    end = dataList[2]
                    fps = dataList[3]
                    interp = dataList[4]
                    sys.__stdout__.write("Export Sequence ------------->: " + str(name) + "\n")

                    try:
                        exportCharacter = dataList[5]
                    except:
                        if len(characters) > 1:
                            characterString = ""
                            for char in characters:
                                characterString += str(char) + " or "
                            result = cmds.promptDialog(
                                title='No Character Data Found',
                                message='Enter Name: ' + characterString,
                                button=['OK', 'Cancel'],
                                defaultButton='OK',
                                cancelButton='Cancel',
                                dismissString='Cancel')

                            if result == 'OK':
                                exportCharacter = cmds.promptDialog(query=True, text=True)
                        else:
                            exportCharacter = characters[0]

                    if interp == "Independent Euler Angle":
                        interp = 1

                    if interp == "Synchronized Euler Angle":
                        interp = 2

                    if interp == "Quaternion Slerp":
                        interp = 3

                    if cmds.checkBox(self.widgets["optionalPathCB"], q=True, v=True):
                        customPath = cmds.textField(self.widgets["ExportPathtextField"], q=True, text=True)
                        filename = os.path.basename(name)
                        exportPath = os.path.join(customPath, filename)
                    else:
                        #directory = os.path.dirname(path)
                        #filename = os.path.basename(name)
                        #exportPath = os.path.join(directory, filename)
                        exportPath = name

                    sys.__stdout__.write("             Final Export Path: " + exportPath + "\n")
                    pre_text = "--- Final Export Path: "
                    self.logger.info(pre_text + exportPath, title=None)
                    if os.path.exists(exportPath):
                        self.logger.warning("OVERWRITTEN: " + exportPath, title=None)
                        self._fbx_overwrites.append(exportPath)
                    if exportPath in self._fbx_files:
                        self.logger.error("DUPLICATE!!!: " + exportPath, title=None)
                        self._duplicates.append(exportPath)
                    self._fbx_files.append(exportPath)

                    startFrame = int(start)
                    endFrame = int(end)

                    cmds.playbackOptions(min = startFrame, animationStartTime = startFrame)
                    cmds.playbackOptions(max = endFrame, animationEndTime = endFrame)
                    sys.__stdout__.write("Start Frame: " + str(startFrame) + "\n")
                    sys.__stdout__.write("End Frame:   " + str(endFrame) + "\n")

                    #custom attrs to export
                    import json

                    if not cmds.objExists("ExportAnimationSettings.settings"):
                        cmds.addAttr("ExportAnimationSettings", ln = "settings", dt = "string")
                        jsonString = json.dumps([False, False, False, "null", "null"])
                        cmds.setAttr("ExportAnimationSettings.settings", jsonString, type = "string")

                    settings = json.loads(cmds.getAttr("ExportAnimationSettings.settings"))

                    #get blendshapes
                    #sys.__stdout__.write("    get blendshapes..." + "\n")
                    cmds.progressBar(self.widgets["currentFileProgressBar"], edit = True, step = step)

                    self.getBlendshapes(step, exportCharacter, startFrame, endFrame)

                    #duplicate the skeleton
                    self.dupeAndBake(step, exportCharacter, startFrame, endFrame, settings[2], settings[4])

                    cmds.select("root", hi = True)
                    skeletonvis = cmds.ls(sl=True)
                    cmds.cutKey(cl=True, at="v")
                    for jnt in skeletonvis:
                        cmds.setAttr(jnt+".v", 1)

                    self.exportFBX(exportPath, interp)

        else:
            for character in characters:
                sys.__stdout__.write("Export Character ------------->: " + str(character) + "\n")
                #add character suffix to fbx path file
                exportPath = path.rpartition(".fbx")[0]
                exportPath = exportPath + "_" + character + ".fbx"

                #get blendshapes
                #sys.__stdout__.write("    get blendshapes..." + "\n")
                cmds.progressBar(self.widgets["currentFileProgressBar"], edit = True, step = step)
                self.getBlendshapes(step, character, startFrame, endFrame)

                #duplicate the skeleton
                self.dupeAndBake(step, character, startFrame, endFrame)

                sys.__stdout__.write("Start Frame: " + str(startFrame) + "\n")
                sys.__stdout__.write("End Frame:   " + str(endFrame) + "\n")

                #check remove root animation checkbox. if true, delete keys off of root and zero out
                removeRoot = cmds.checkBox(self.widgets["removeRoot"], q = True, v = True)
                if removeRoot:
                    cmds.select("root")
                    cmds.cutKey()
                    for attr in ["tx", "ty", "tz", "rx", "ry", "rz"]:
                        cmds.setAttr("root." + attr, 0)
                self.logger.info(exportPath, title=None)
                if os.path.exists(exportPath):
                    self.logger.warning("OVERWRITTEN: " + exportPath, title=None)
                    self._fbx_overwrites.append(exportPath)
                if exportPath in self._fbx_files:
                    self.logger.error("DUPLICATE!: " + exportPath, title=None)
                    self._duplicates.append(exportPath)
                self._fbx_files.append(exportPath)
                self.exportFBX(exportPath, interp)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def exportFBX(self, path, interp, *args):
        if cmds.objExists("root"):
            #sys.__stdout__.write("    FBX Export...\n")

           #export selected
            #first change some fbx properties
            string = "FBXExportConstraints -v 1;"
            string += "FBXExportCacheFile -v 0;"
            mel.eval(string)

            cmds.select("root", hi = True)
            if cmds.objExists("custom_export"):
                cmds.select("custom_export", add = True)

            newpath = path.replace(path.split("/")[-1], "")
            print "NEW PATH ", newpath
            if not os.path.exists(newpath):
                os.makedirs(newpath)

            cmds.file(path, es = True, force = True, prompt = False, type = "FBX export")

            #clean scene
            cmds.delete("root")
            if cmds.objExists("custom_export"):
                cmds.delete("custom_export")

        #reset rotation interp
        cmds.optionVar(iv = ("rotationInterpolationDefault", interp))
        sys.__stdout__.write("   FBX Exported Successfully!!: " + path + "\n")

