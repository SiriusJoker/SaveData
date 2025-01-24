import maya.cmds as cmds
import maya.mel as mel
import os
from datetime import datetime
import traceback
from error_utils import show_error_window

def take_screenshot_with_hidden_geometry(filepath):

    # Get name and path to output file
    filename = os.path.basename(filepath)
    raw_name = os.path.splitext(filename)[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    workspace_dir = cmds.workspace(query=True, rd=True)
    export_folder = os.path.join(workspace_dir, "images/screenshots/")
    os.makedirs(export_folder, exist_ok=True)
    screenshot_path = os.path.join(export_folder, f"{raw_name}_{timestamp}.png")

    # Get all geometry objects in the scene
    geometry = cmds.ls(type="mesh")

    # Save the current visibility and intermediateObject states
    visibility_states = {}
    intermediate_states = {}

    for obj in geometry:
        transform = cmds.listRelatives(obj, parent=True, fullPath=True)[0]
        visibility_states[transform] = cmds.getAttr(f"{transform}.visibility")
        intermediate_states[obj] = cmds.getAttr(f"{obj}.intermediateObject")

    # Unhide all geometry (visibility and intermediateObject)
    for obj in geometry:
        transform = cmds.listRelatives(obj, parent=True, fullPath=True)[0]
        cmds.setAttr(f"{transform}.visibility", True)
        cmds.setAttr(f"{obj}.intermediateObject", False)

    # Refresh the viewport to apply changes
    cmds.refresh()

    # Take a playblast screenshot
    current_panel = cmds.getPanel(withFocus=True)
    if cmds.getPanel(typeOf=current_panel) == "modelPanel":
        # Configure panel to show everything
        cmds.modelEditor(current_panel, edit=True, displayAppearance="smoothShaded", allObjects=True)
        mel.eval(
            f"playblast -fp 4 -format image -completeFilename \"{screenshot_path}\" -widthHeight 1920 1080 -showOrnaments false -viewer false")
    else:
        message = f"Please focus on a viewport panel (e.g., Perspective view) before running the script."
        print(message)
        error_details = traceback.format_exc()
        show_error_window(error_details, message)

    # Restore original visibility and intermediateObject states
    for obj in geometry:
        transform = cmds.listRelatives(obj, parent=True, fullPath=True)[0]
        cmds.setAttr(f"{transform}.visibility", visibility_states[transform])
        cmds.setAttr(f"{obj}.intermediateObject", intermediate_states[obj])
    return screenshot_path