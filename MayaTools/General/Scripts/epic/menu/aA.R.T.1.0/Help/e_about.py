NICENAME = "About"
def __run_it__():
    from maya import cmds
    message = """(c) Epic Games, Inc. 2013\nCreated by: Jeremy Ernst\njeremy.ernst@epicgames.com\nVisit www.epicgames.com"""
    cmds.confirmDialog(title="About", message=message, icon="information")
