import maya.cmds as cmds
import maya.mel as mel
import os, cPickle, sys
from functools import partial
from epic.menu import epic_menu

def customMayaMenu():
    """Procedurally build Epic Menu and check for source control."""
    add_to_python_path()
    use_source_control = checkSourceControl()
    gMainWindow = mel.eval('$temp1=$gMainWindow')
    menus = cmds.window(gMainWindow, q=True, menuArray=True)
    if not use_source_control:
        return build_epic_menu("Perforce")
    if "eUtils" not in menus:
        build_epic_menu()

def build_epic_menu(ignore=None, *args):
    epic_menu.EpicMenu.epic_reload(ignore)

def checkSourceControl():
    """Check for Source control."""
    toolsPath = cmds.internalVar(usd = True) + "mayaTools.txt"
    if os.path.exists(toolsPath):

        f = open(toolsPath, 'r')
        mayaToolsDir = f.readline()
        f.close()

        settingsLocation = mayaToolsDir + "/General/Scripts/projectSettings.txt"
        if os.path.exists(settingsLocation):
            f = open(settingsLocation, 'r')
            settings = cPickle.load(f)
            f.close()

            #find use source control value
            sourceControl = settings.get("UseSourceControl")
            if sourceControl:
                return True
#############################################################################################
#############################################################################################
#############################################################################################
def add_to_python_path():
    """Adds ARTv1 to the python path"""
    mayaToolsDir = mayaToolsPath()
    plugin_path = "{0}/General/Scripts/plug-ins".format(mayaToolsDir)
    if mayaToolsDir:
        # add ARTv1 to the python path
        sys.path.append("{0}/General/Scripts/art_v1".format(mayaToolsDir))
        sys.path.append("{0}/General/Scripts/third_party".format(mayaToolsDir))
        os.environ["MAYA_PLUG_IN_PATH"] += str(";" + plugin_path)
#############################################################################################
#############################################################################################
#############################################################################################
def mayaToolsPath():
    toolsPath = cmds.internalVar(usd = True) + "mayaTools.txt"
    mayaToolsDir = None
    if os.path.exists(toolsPath):

        f = open(toolsPath, 'r')
        mayaToolsDir = f.readline()
        f.close()
    return mayaToolsDir
#############################################################################################
#############################################################################################
#############################################################################################
def setProj(projectName, *args):
    import perforceUtils
    reload(perforceUtils)
    perforceUtils.setCurrentProject(projectName)

#############################################################################################
#############################################################################################
#############################################################################################
def editProj(projectName, *args):
    import perforceUtils
    reload(perforceUtils)
    perforceUtils.editProject(projectName)

#############################################################################################
#############################################################################################
#############################################################################################
def createNewProj(*args):
    import perforceUtils
    reload(perforceUtils)
    perforceUtils.createNewProject()

#############################################################################################
#############################################################################################
#############################################################################################
def autoUpdateTools(*args):
    import perforceUtils
    reload(perforceUtils)
    perforceUtils.p4_checkForUpdates()


#############################################################################################
#############################################################################################
#############################################################################################
def launchARTSettings(*args):
    import ART_Settings
    reload(ART_Settings)
    ART_Settings.ART_Settings()

#############################################################################################
#############################################################################################
#############################################################################################
def aboutARTTools(*args):

    cmds.confirmDialog(title = "About", message = "(c) Epic Games, Inc. 2013\nCreated by: Jeremy Ernst\njeremy.ernst@epicgames.com\nVisit www.epicgames.com", icon = "information")

#############################################################################################
#############################################################################################
#############################################################################################
def editCharacter(*args):

    if cmds.window("artEditCharacterUI", exists = True):
        cmds.deleteUI("artEditCharacterUI")

    window = cmds.window("artEditCharacterUI", w = 300, h = 400, title = "Edit Character", mxb = False, mnb = False, sizeable = True)
    mainLayout = cmds.columnLayout(w = 300, h = 400, rs = 5, co = ["both", 5])

    #banner image
    toolsPath = cmds.internalVar(usd = True) + "mayaTools.txt"
    if os.path.exists(toolsPath):

        f = open(toolsPath, 'r')
        mayaToolsDir = f.readline()
        f.close()

    cmds.image(w = 300, h = 50, image = mayaToolsDir + "/General/Icons/ART/artBanner300px.bmp", parent = mainLayout)

    cmds.text(label = "", h = 1, parent = mainLayout)
    optionMenu = cmds.optionMenu("artProjOptionMenu", label = "Project:", w =290, h = 40, cc = getProjCharacters, parent = mainLayout)
    textScrollList = cmds.textScrollList("artProjCharacterList", w = 290, h = 300, parent = mainLayout)
    button = cmds.button(w = 290, h = 40, label = "Edit Export File", c = editSelectedCharacter, ann = "Edit the character's skeleton settings, joint positions, or skin weights.", parent = mainLayout)
    button2 = cmds.button(w = 290, h = 40, label = "Edit Rig File", c = editSelectedCharacterRig, ann = "Edit the character's control rig that will be referenced in by animation.", parent = mainLayout)

    cmds.text(label = "", h = 1)


    cmds.showWindow(window)
    getProjects()

   # CRA NEW CODE - Adding the code snippet so that it starts in your favorite folder.
    #set favorite project if it exists
    settingsLocation = mayaToolsDir + "/General/Scripts/projectSettings.txt"
    if os.path.exists(settingsLocation):
        f = open(settingsLocation, 'r')
        settings = cPickle.load(f)
        favoriteProject = settings.get("FavoriteProject")

        try:
            cmds.optionMenu("artProjOptionMenu", edit = True, v = favoriteProject)
        except:
            pass
    # CRA END NEW CODE
    getProjCharacters()

#############################################################################################
#############################################################################################
#############################################################################################
def getProjects(*args):

    toolsPath = cmds.internalVar(usd = True) + "mayaTools.txt"
    if os.path.exists(toolsPath):

        f = open(toolsPath, 'r')
        mayaToolsDir = f.readline()
        f.close()

    projects = os.listdir(mayaToolsDir + "/General/ART/Projects/")
    for project in projects:
        cmds.menuItem(label = project, parent = "artProjOptionMenu")

#############################################################################################
#############################################################################################
#############################################################################################
def getProjCharacters(*args):
    toolsPath = cmds.internalVar(usd = True) + "mayaTools.txt"
    if os.path.exists(toolsPath):

        f = open(toolsPath, 'r')
        mayaToolsDir = f.readline()
        f.close()

    proj = cmds.optionMenu("artProjOptionMenu", q = True, value = True)

    cmds.textScrollList("artProjCharacterList", edit = True, removeAll = True)
    characters = os.listdir(mayaToolsDir + "/General/ART/Projects/" + proj + "/ExportFiles/")

    for character in characters:
        if os.path.isfile(mayaToolsDir + "/General/ART/Projects/" + proj + "/ExportFiles/" + character):
            if character.rpartition(".")[2] == "mb":
                niceName = character.rpartition(".")[0]
                niceName = niceName.partition("_Export")[0]
                cmds.textScrollList("artProjCharacterList", edit = True, append = niceName)

#############################################################################################
#############################################################################################
#############################################################################################
def editSelectedCharacter(*args):
    toolsPath = cmds.internalVar(usd = True) + "mayaTools.txt"
    if os.path.exists(toolsPath):

        f = open(toolsPath, 'r')
        mayaToolsDir = f.readline()
        f.close()

    proj = cmds.optionMenu("artProjOptionMenu", q = True, value = True)
    character = cmds.textScrollList("artProjCharacterList", q = True, si = True)[0]

    cmds.file(mayaToolsDir + "/General/ART/Projects/" + proj + "/ExportFiles/" + character + "_Export.mb", open = True, force = True)
    cmds.deleteUI("artEditCharacterUI")
    launchSkeletonBuilder()


#############################################################################################
#############################################################################################
#############################################################################################
def editSelectedCharacterRig(*args):
    toolsPath = cmds.internalVar(usd = True) + "mayaTools.txt"
    if os.path.exists(toolsPath):

        f = open(toolsPath, 'r')
        mayaToolsDir = f.readline()
        f.close()

    proj = cmds.optionMenu("artProjOptionMenu", q = True, value = True)
    character = cmds.textScrollList("artProjCharacterList", q = True, si = True)[0]

    cmds.file(mayaToolsDir + "/General/ART/Projects/" + proj + "/AnimRigs/" + character + ".mb", open = True, force = True)
    cmds.deleteUI("artEditCharacterUI")
    launchSkeletonBuilder()



#############################################################################################
#############################################################################################
#############################################################################################
def changeMayaToolsLoc(*args):
    path = cmds.internalVar(usd = True) + "mayaTools.txt"
    if os.path.exists(path):
        os.remove(path)
        cmds.confirmDialog(title = "Change Location", message = "Once you have chosen your new tools location, it is recommended that you restart Maya.", button = "OK")
        cmds.file(new = True, force = True)

#############################################################################################
#############################################################################################
#############################################################################################
def launchSkeletonBuilder(*args):

    import ART_skeletonBuilder_UI
    reload(ART_skeletonBuilder_UI)
    UI = ART_skeletonBuilder_UI.SkeletonBuilder_UI()


#############################################################################################
#############################################################################################
#############################################################################################
def launchAddCharacter(*args):

    import ART_addCharacter_UI
    reload(ART_addCharacter_UI)
    UI = ART_addCharacter_UI.AddCharacter_UI()


#############################################################################################
#############################################################################################
#############################################################################################
def launchAnimUI(*args):

    import ART_animationUI
    reload(ART_animationUI)
    UI = ART_animationUI.AnimationUI()

#############################################################################################
#############################################################################################
#############################################################################################
def launchEpic(*args):

    cmds.launch(web="http://www.epicgames.com")

#############################################################################################
#############################################################################################
#############################################################################################
def launchUnreal(*args):

    cmds.launch(web="http://www.unrealengine.com")

#############################################################################################
#############################################################################################
#############################################################################################
def launchAnimHelp(*args):

    toolsPath = cmds.internalVar(usd = True) + "mayaTools.txt"
    if os.path.exists(toolsPath):

        f = open(toolsPath, 'r')
        mayaToolsDir = f.readline()
        f.close()


    if os.path.exists(mayaToolsDir + "/General/ART/Help/ART_AnimHelp.pdf"):
        cmds.launch(pdfFile = mayaToolsDir + "/General/ART/Help/ART_AnimHelp.pdf")

#############################################################################################
#############################################################################################
#############################################################################################
def launchRigHelp(self, *args):

    cmds.launch(web = "https://docs.unrealengine.com/latest/INT/Engine/Content/Tools/MayaRiggingTool/index.html")


#############################################################################################
#############################################################################################
#############################################################################################
def launchLearningVideos(self, *args):

    import ART_Help
    reload(ART_Help)
    ART_Help.ART_LearningVideos()


#############################################################################################
#############################################################################################
#############################################################################################
def setupScene(*args):

    cmds.currentUnit(time = 'ntsc')
    cmds.playbackOptions(min = 0, max = 100, animationStartTime = 0, animationEndTime = 100)
    cmds.currentTime(0)


    #check for skeleton builder or animation UIs
    if cmds.dockControl("skeletonBuilder_dock", exists = True):
        print "Custom Maya Menu: SetupScene"
        channelBox = cmds.formLayout("SkelBuilder_channelBoxFormLayout", q = True, childArray = True)
        if channelBox != None:
            channelBox = channelBox[0]

            #reparent the channelBox Layout back to maya's window
            cmds.control(channelBox, e = True, p = "MainChannelsLayersLayout")
            channelBoxLayout = mel.eval('$temp1=$gChannelsLayersForm')
            channelBoxForm = mel.eval('$temp1 = $gChannelButtonForm')

            #edit the channel box pane's attachment to the formLayout
            cmds.formLayout(channelBoxLayout, edit = True, af = [(channelBox, "left", 0),(channelBox, "right", 0), (channelBox, "bottom", 0)], attachControl = (channelBox, "top", 0, channelBoxForm))


        #print "deleting dock and window and shit"
        cmds.deleteUI("skeletonBuilder_dock")
        if cmds.window("SkelBuilder_window", exists = True):
            cmds.deleteUI("SkelBuilder_window")





    if cmds.dockControl("artAnimUIDock", exists = True):

        channelBox = cmds.formLayout("ART_cbFormLayout", q = True, childArray = True)
        if channelBox != None:
            channelBox = channelBox[0]

            #reparent the channelBox Layout back to maya's window
            cmds.control(channelBox, e = True, p = "MainChannelsLayersLayout")
            channelBoxLayout = mel.eval('$temp1=$gChannelsLayersForm')
            channelBoxForm = mel.eval('$temp1 = $gChannelButtonForm')

            #edit the channel box pane's attachment to the formLayout
            cmds.formLayout(channelBoxLayout, edit = True, af = [(channelBox, "left", 0),(channelBox, "right", 0), (channelBox, "bottom", 0)], attachControl = (channelBox, "top", 0, channelBoxForm))


        #print "deleting dock and window and shit"
        cmds.deleteUI("artAnimUIDock")
        if cmds.window("artAnimUI", exists = True):
            cmds.deleteUI("artAnimUI")


#############################################################################################
#############################################################################################
#############################################################################################
def autoOpenAnimUI():
    if cmds.objExists("*:master_anim_space_switcher_follow"):
        launchAnimUI()


#############################################################################################
#############################################################################################
#############################################################################################
def p4GetLatest(*args):
    import perforceUtils
    reload(perforceUtils)
    perforceUtils.p4_getLatestRevision(None)


#############################################################################################
#############################################################################################
#############################################################################################
def p4CheckOut(*args):
    import perforceUtils
    reload(perforceUtils)
    perforceUtils.p4_checkOutCurrentFile(None)

#############################################################################################
#############################################################################################
#############################################################################################
def p4GetHistory(*args):
    import perforceUtils
    reload(perforceUtils)
    perforceUtils.p4_getRevisionHistory()


#############################################################################################
#############################################################################################
#############################################################################################
def p4Submit(*args):
    import perforceUtils
    reload(perforceUtils)
    perforceUtils.p4_submitCurrentFile(None, None)


#############################################################################################
#############################################################################################
#############################################################################################
def p4AddSubmit(*args):
    import perforceUtils
    reload(perforceUtils)
    perforceUtils.p4_addAndSubmitCurrentFile(None, None)


#############################################################################################
#############################################################################################
#############################################################################################
def export_selected_skin_weights(surpress=None, *args):
    """
    Exports out weights for selected geometry.
        REF: acarlisle
    NOTE: Batch option to overwrite all.
    """
    # selection check
    selection = cmds.ls(sl=True)
    title = "Export Skin Weights"

    # args, kwargs
    buttons = ["Overwrite", "Overwrite All", "Skip", "Cancel"]
    kwargs = {"icon": "warning", "title": title, "message": "Nothing Selected"}
    if not selection:
        return cmds.confirmDialog(**kwargs)

    # tool path check
    tools_path = cmds.internalVar(usd=True) + "mayaTools.txt"
    if not os.path.exists(tools_path):
        return cmds.error("Could not find tools path!")

    # find path
    tools_file = open(tools_path, 'r')
    maya_tools_dir = tools_file.readline()
    tools_file.close()

    # skin weights_path
    skin_weights_path = "{0}\General\ART\SkinWeights\\".format(maya_tools_dir)
    if not os.path.exists(skin_weights_path):
        os.makedirs(skin_weights_path)

    # export
    batch = False
    for geo in selection:
        path = "{0}{1}.txt".format(skin_weights_path, geo)
        if not os.path.exists(path):
            doSkinWeightExport(geo, path, False)
            continue
        kwargs["icon"] = "question"
        kwargs["message"] = "{0} already exists".format(path)
        kwargs["button"] = buttons
        if not surpress:
            if not batch:
                overwrite_check = cmds.confirmDialog(**kwargs)
                if overwrite_check == "Overwrite All":
                    batch = True
                elif overwrite_check == "Cancel":
                    return "Weight Exporting Canceled."
                doSkinWeightExport(geo, path, False)
                continue
            doSkinWeightExport(geo, path, False)
            continue
        # if surpress
        doSkinWeightExport(geo, path, True)
    return "Weights Exported."

def exportSkinWeights(*args):

    #tools path
    toolsPath = cmds.internalVar(usd = True) + "mayaTools.txt"
    if os.path.exists(toolsPath):

        f = open(toolsPath, 'r')
        mayaToolsDir = f.readline()
        f.close()

        path = None

    selection = cmds.ls(sl = True)
    if selection == []:
        cmds.confirmDialog(icon = "warning", title = "Export Skin Weights", message = "Nothing Selected")
        return
    else:
        for one in selection:

            #add a dialog that warns the user that they may lose weighting information if their changes are drastic
            result = cmds.promptDialog(title = "Export Weights", text = one, message = "FileName:", button = ["Accept", "Cancel"])
            if result == "Accept":
                name = cmds.promptDialog(q = True, text = True)

                path = mayaToolsDir + "\General\ART\SkinWeights\\"
                if not os.path.exists(path):
                    os.makedirs(path)

                path = path + name + ".txt"

                if not os.path.exists(path):
                    doSkinWeightExport(one, path)
                else:
                    result = cmds.confirmDialog(icon = "question", title = "Export Weights", message = path+" already exists.", button = ["Overwrite", "Cancel"])
                    if result == "Overwrite":
                        doSkinWeightExport(one, path)
                        #print "saved skin weights for " + one + " to " + path

    print "EXPORT WEIGHTS DONE!"

def doSkinWeightExport(one, path):
    #find geo by looking at skinclusters
    skinClusters = cmds.ls(type = 'skinCluster')

    print "saved skin weights for " + one + " to " + path
    for skin in skinClusters:

        #go through each found skin cluster, and if we find a skin cluster whose geometry matches our selection, get influences
        bigList = []

        for cluster in skinClusters:
            geometry = cmds.skinCluster(cluster, q = True, g = True)[0]

            geoTransform = cmds.listRelatives(geometry, parent = True)[0]

            if geoTransform == one:
                f = open(path, 'w')

                skinCluster = cluster

                #find all vertices in the current geometry
                verts = cmds.polyEvaluate(one, vertex = True)

                for i in range(int(verts)):
                    #get weighted transforms
                    transforms = cmds.skinPercent( skinCluster, one + ".vtx[" + str(i) + "]", ib = .001, query=True, t= None)


                    #get skinPercent value per transform
                    values = cmds.skinPercent( skinCluster, one + ".vtx[" + str(i) + "]", ib = .001, query=True, value=True)
                    list = []
                    list.append(i)

                    for x in range(int(len(values))):
                        list.append([transforms[x], values[x]])

                    #add each vert info's transforms, and values to the overall huge list
                    bigList.append(list)

                #write that overall list to file
                cPickle.dump(bigList, f)

                #close the file
                f.close()

                #operation complete
                cmds.headsUpMessage( "Skin Weights Exported!", time=3.0 )

                return



#############################################################################################
#############################################################################################
#############################################################################################
def importSkinWeights(*args):

    #tools path
    toolsPath = cmds.internalVar(usd = True) + "mayaTools.txt"
    if os.path.exists(toolsPath):

        f = open(toolsPath, 'r')
        mayaToolsDir = f.readline()
        f.close()


    selection = cmds.ls(sl = True)
    if selection == []:
        cmds.confirmDialog(icon = "warning", title = "Import Skin Weights", message = "Nothing Selected")
        return


    if selection != []:
        if len(selection) > 1:
            cmds.confirmDialog(icon = "warning", title = "Import Skin Weights", message = "Too many objects selected. Please only selected 1 mesh.")
            return


        #find all files in the system dir
        path = mayaToolsDir + "\General\ART\SkinWeights\\"

        try:
            fileToImport = cmds.fileDialog2(fileFilter="*.txt", dialogStyle=2, fm = 1, startingDirectory = path)[0]

        except:
            cmds.warning("Operation Cancelled.")
            return



        #load the file with cPickle and parse out the information
        file = open(fileToImport, 'r')
        weightInfoList = cPickle.load(file)


        #get the number of vertices in the mesh. This will be used to update our progress window
        verts = cmds.polyEvaluate(selection[0], vertex = True)
        if verts < 20:
            verts = verts * 20

        increment = int(verts/20)
        matchNum = increment

        #find the transforms from the weightInfoList. format = [ [vertNum, [jointName, value], [jointName, value] ] ]
        transforms = []
        newList = weightInfoList[:]
        for info in newList:

            for i in info:
                if i != info[0]:
                    transform = i[0]
                    transforms.append(transform)

        #remove duplicates from the transforms list
        transforms = set(transforms)

        #clear selection. Add transforms to selection and geo
        cmds.select(clear = True)
        for t in transforms:
            if cmds.objExists(t):
                cmds.select(t, add = True)


        #check if the geometry that is selected is already skinned or not
        skinClusters = cmds.ls(type = 'skinCluster')
        skinnedGeometry = []
        for cluster in skinClusters:
            geometry = cmds.skinCluster(cluster, q = True, g = True)[0]
            geoTransform = cmds.listRelatives(geometry, parent = True)[0]
            skinnedGeometry.append(geoTransform)

            if geoTransform == selection[0]:
                skin = cluster


        #if a skin cluster does not exist already on the mesh:
        if selection[0] not in skinnedGeometry:

            #put a skin cluster on the geo normalizeWeights = 1, dr=4.5, mi = 4,
            cmds.select(selection[0], add = True)
            skin = cmds.skinCluster( tsb = True, skinMethod = 0, name = (selection[0] +"_skinCluster"))[0]


        #setup a progress window to track length of progress
        cmds.progressWindow(title='Skin Weights', progress = 0, status = "Reading skin weight information from file...")

        #get the vert number, and the weights for that vertex
        for info in weightInfoList:
            vertNum = info[0]
            info.pop(0)

            #progress bar update
            if vertNum == matchNum:
                cmds.progressWindow( edit=True, progress = ((matchNum/increment) * 5), status=  "Importing skin weights for " + selection[0] + ".\n Please be patient")
                matchNum += increment

            #set the weight for each vertex
            try:
                cmds.skinPercent(skin, selection[0] + ".vtx[" + str(vertNum) + "]", transformValue= info)
            except:
                pass


        #close the file
        file.close()

        #close progress window
        cmds.progressWindow(endProgress = 1)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#LAUNCH SCRIPT JOBS
scriptJobNum2 = cmds.scriptJob(event = ["PostSceneRead", autoOpenAnimUI])
scriptJobNum = cmds.scriptJob(event = ["NewSceneOpened", setupScene])
