import maya.cmds as cmds
import json
import os
from datetime import datetime
from collections import namedtuple
from PySide2 import QtWidgets
import traceback

out_name_path=namedtuple('out_name_path',['raw_name','output_path'])

def show_error_window(error_message, message):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)
    msg_box.setWindowTitle("Error")
    msg_box.setText("The script Save_data_to_json encountered an error. \n" + message)
    msg_box.setDetailedText(error_message)
    msg_box.exec_()

def load_config(config_path):
    try:
        with open(config_path, "r") as config_file:
            return json.load(config_file)
    except Exception as e:
        message = f"Error loading configuration: {e}"
        print(message)
        error_details = traceback.format_exc()
        show_error_window(error_details,message)
        return {}

def get_output_path(filepath):

    # Get name and path to output file
    filename = os.path.basename(filepath)
    raw_name = os.path.splitext(filename)[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    workspace_dir = cmds.workspace(query=True, rd=True)
    export_folder = os.path.join(workspace_dir, "ExportedData")
    os.makedirs(export_folder, exist_ok=True)
    output_path=os.path.join(export_folder, f"scene_poly_data_{raw_name}_{timestamp}.json")
    return out_name_path(raw_name, output_path)

def get_poly_data(poly_objects,config):
    data_obj = {}
    for obj in poly_objects:
        try:
            transform = cmds.listRelatives(obj, parent=True, fullPath=True)[0]
            children = cmds.listRelatives(transform, children=True, fullPath=True) or []
            display_layers = cmds.listConnections(transform, type="displayLayer") or []
            vertex_count = cmds.polyEvaluate(obj, vertex=True)
            edge_count = cmds.polyEvaluate(obj, edge=True)
            face_count = cmds.polyEvaluate(obj, face=True)
            triangle_count = cmds.polyEvaluate(obj, triangle=True)
            uv_shell_count = cmds.polyEvaluate(obj, uvShell=True)
            visibility = cmds.getAttr(f"{obj}.visibility")
            children_count = len(children)
            parentt = cmds.listRelatives(transform, parent=True, fullPath=True)
            groups = parentt[0] if parentt and cmds.objectType(parentt[0]) else None

            obj_data = {}
            if config.get("save_vertex_count", False):
                obj_data["vertex_count"] = vertex_count
            if config.get("save_edge_count", False):
                obj_data["edge_count"] = edge_count
            if config.get("save_face_count", False):
                obj_data["face_count"] = face_count
            if config.get("save_triangle_count", False):
                obj_data["triangle_count"] = triangle_count
            if config.get("save_uv_shell_count", False):
                obj_data["uv_shell_count"] = uv_shell_count
            if config.get("save_visibility", False):
                obj_data["visibility"] = visibility
            if config.get("save_children_count", False):
                obj_data["children_count"] = children_count
            if config.get("save_display_layers", False):
                obj_data["display_layers"] = display_layers if display_layers else 0
            if config.get("save_groups", False):
                obj_data["groups"] = groups

            data_obj[transform] = obj_data
        except Exception as e:
            message = f"Error processing object {obj}: {e}"
            print(message)
            error_details = traceback.format_exc()
            show_error_window(error_details, message)
            continue
    return data_obj

def export_poly_data_to_json():

    script_directory = cmds.internalVar(userScriptDir=True)

    config_path = os.path.join(script_directory, "SaveData/config.json") 
    config=load_config(config_path)

    # Get current scene
    filepath = cmds.file(q=True, sn=True)
    if not filepath:
        message = "No scene file is currently open. Maybe you need to save the scene and try again"
        print(message)
        error_details = traceback.format_exc()
        show_error_window(error_details, message)
        return

    out_name_path=get_output_path(filepath)
    raw_name, output_path=out_name_path;

    # Get data for polygonal objects
    poly_objects = cmds.ls(type="mesh", long=True)
    if not poly_objects:
        message = "No polygonal objects found in the scene."
        print(message)
        error_details = traceback.format_exc()
        show_error_window(error_details, message)

    data_obj = get_poly_data(poly_objects,config)

    
    # Get data for scene
    file_size = os.path.getsize(filepath)
    completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    scene_data = {
        "scene_name": raw_name,
        "scene_size (bytes)": file_size,
        "completion_time": completion_time,
    }
    
    data = {
        "Polygonal objects data": data_obj,
        "Scene data": scene_data
    }
    
    # Write data
    try:
        with open(output_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data exported successfully to {output_path}")
    except Exception as e:
        message = f"Failed to write JSON file: {e}"
        print(message)
        error_details = traceback.format_exc()
        show_error_window(error_details, message)

export_poly_data_to_json()
