
# 'Script Runner' - Copyright (2013-2019) Good Spirit Graphics (www.goodspiritgraphics.com)


# ##### BEGIN GPL LICENSE BLOCK #####
#
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####



# <pep8-80 compliant>



#====================Version History====================
#   1.0     Initial release.
#   1.1     Added error message handling and processing.
#   1.2     Added seamless handling of  modules/addons using '__name__' 
#   1.3     Added option to set the number of scriipts from the panels. 
#             Quieted down the 'Cancel' icon.
#   1.4     Updated for Blender 2.8x  
#             Added a button to load all files in a directory.
#             Increased script slots to 100.
#   1.5     Added save panel state: Numer of displayed slots, and slot paths are saved.
#====================================================



bl_info = {
           "name": "Script Runner",
           "author": "Christopher Barrett (www.goodspiritgraphics.com)",
           "version": (1, 5),
           "blender": (2, 80, 0),
           "api": 58537,
           "location": "File > Import > GSG Script Runner - (.py), & '3D View Tool Shelf', & 'Text Editor Tool Shelf'.",
           "description": "Run a python script from any file directory.",
           "warning": "",
           "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Import-Export/Script_Runner",
           "tracker_url": "",
           "category": "Import-Export"
          }




from bpy_extras.io_utils import ImportHelper
import bpy
import os, sys, platform
import pickle
import shutil
import fnmatch
import errno
import ntpath
import traceback
import importlib
import string
import random

from bpy.types import Operator, AddonPreferences
from bpy.props import EnumProperty, StringProperty,BoolProperty, IntProperty, FloatVectorProperty


gl_num_slots        = 100
gl_path_data_file   = 'script_runner_data.mbl'
gl_paths_loaded     = False


#------------------------------Version compatibility
if True:
    if bpy.app.version >= (2, 80):
        file_icon = 'FILEBROWSER'
    else:
        file_icon = 'FILESEL'

        
    def GetUserPreferences():
        if bpy.app.version >= (2, 80):
            user_settings = bpy.context.preferences.addons[__name__].preferences
        else:
            user_settings = bpy.context.user_preferences.addons[__name__].preferences
            
        return user_settings
        

        
        

#------------------------------Preferences
def CallBack(self, context):
    # This triggers on load, and clears out the paths before they are retrieved.
    
    
    if gl_paths_loaded:
        print ('CallBack')
        # Blender sometimes saves the number of displayed slots on its own, but it is inconsistent.
        SaveSlots()
    
    
class ScriptRunnerAddonPreferences(AddonPreferences):
    bl_idname = __name__ 
    
    error_msg_verbose = BoolProperty(name="error_msg_verbose", default = False)
    display_num_scripts = BoolProperty(name="display_num_scripts", default = True)
    display_3d = BoolProperty(name="display_3d", default = True)
    display_text_editor = BoolProperty(name="display_text_editor", default = True)
    num_scripts = IntProperty(name="Number of Scripts", description = "Set to the number of scripts to display in the panel", min = 1, max = gl_num_slots, default = 2, update = CallBack)
    
    script_paths = []
    for num_path in range(0, gl_num_slots):
        script_paths.append("")
        
    
    
    def draw(self, context):
        user_settings = GetUserPreferences()
        
        
        layout = self.layout
        split = layout.split()
                        
        #-----Column 1
        col1 = split.column()
        row = col1.row()
        row.label(text = "Display Area: (Restart required)")
        row = col1.row()
        row.prop(self, "display_3d", text="3D View Toolshelf", toggle = True)
        row = col1.separator()
        row = col1.row()
        row.prop(self, "display_text_editor", text="Text Editor Toolshelf", toggle = True)

        #-----Column 2
        col2 = split.column()
        row = col2.row()
        row.label(text = "Number of Script Slots to Display:")
        row = col2.row()
        row.prop(self, "num_scripts", text="Displayed Scripts", slider = False)
        row = col2.row()
        row.prop(self,  "display_num_scripts", text="Display scripts slider on panels", toggle = False)
        
        #-----Column 3
        col3 = split.column()
        row = col3.row()
        row.prop(self, "error_msg_verbose", text="Verbose Error Messages", toggle = False)
 
        row = layout.separator()
        row = layout.row()
        row.label(text = "Script File Paths:")
        box = layout.box()
        row = box.row()
        
        
        for num_path in range(0, gl_num_slots): 
            row.label(text = "File #" + str(num_path + 1) + ":    " + user_settings.script_paths[num_path])
            row = box.row()
        
        
def DrawScriptsSlider(self, context):
    if bpy.app.version >= (2, 80):
        self.layout.prop(context.preferences.addons['script_runner'].preferences, "num_scripts",  text="Displayed Scripts")
    else:
        self.layout.prop(context.user_preferences.addons['script_runner'].preferences, "num_scripts",  text="Displayed Scripts")


def DrawLayout(self, context):        
        user_settings = GetUserPreferences()
        
       
        if user_settings.display_num_scripts: 
            #Copy the slider from the addon user preferences.
            DrawScriptsSlider(self, context)
        
        
        layout = self.layout; 
        row = layout.row()
        
        layout_split = layout.split()

        #Column 1
        col1 = layout_split.column(align = True)
        row = col1.row()
        split = row.split()
        col = split.column()
        col.operator("object.load_directory", text = "Load Directory", icon=file_icon)
        
        #Column 2
        col2 = layout_split.column(align = True)
        row = col2.row()
        split = row.split()
        col = split.column()
        col.operator("object.clear_slots", text = "Clear all Scripts")            
        
        
        row = layout.row()
        
        
        for row_num in range(1, user_settings.num_scripts + 1): 
            pth = user_settings.script_paths[row_num - 1]
        
            #Script 1
            row = layout.row(align = True)
            slot_0_load = row.operator("object.script_load", text = "", icon=file_icon)
            slot_0_load.script_slot = row_num
            
            slot_0_clear = row.operator("object.script_clear", text = "", icon='X')
            slot_0_clear.script_slot = row_num - 1

            if pth != "": 
                label = PathLeaf(pth)
            else:
                label = ""    
                    
            slot_0_run = row.operator("object.script_run", text = label)
            slot_0_run.script_slot = row_num - 1





#-------------------------------Panels

class GSG_PT_script_runner_panel_1(bpy.types.Panel):
    bl_label = "Script Runner"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_context = "WINDOW"
    bl_options = {'DEFAULT_CLOSED'}
           
    
    def draw(self, context):
        DrawLayout(self, context)
        
     

class GSG_PT_script_runner_panel_2(bpy.types.Panel):
    bl_label = "Script Runner"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS" if bpy.app.version < (2, 80) else 'UI'
    # bl_context = "WINDOW"
    bl_options = {'DEFAULT_CLOSED'}
        
    
    def draw(self, context):
        DrawLayout(self, context)
        
        

        
        
#-------------------------------Operators    


#------Menu (main program operation)

class GSG_OT_ScriptRunner(bpy.types.Operator, ImportHelper):
    bl_idname = "file.run_script";
    bl_label = "Run Script";
    
    
    filter_glob = StringProperty(
            default="*.py",
            options={'HIDDEN'},
            )

    filename_ext = ".py";



    def execute(self, context):
                
        if (self.filepath == ""):
            pass
        
        else:
            #Check if file exists, could be a path.
            if os.path.isfile(self.filepath):
                GSG_OT_ScriptRunner.checkDir(self.filepath)    
        
        return {'FINISHED'}
                               
                          
    def checkDir(file_path):
               
        try:
            error = 0
            script_path = os.path.join( bpy.utils.script_path_user() ,  "modules")
            error = 1
            cache_path = os.path.join( bpy.utils.script_path_user() , "modules" )
            cache_path = os.path.join( cache_path,  "__pycache__"  )
            error = 2
            old_name = PathLeaf(file_path).split(".")[0]
            new_name = "script_runner_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10)) + "_" + old_name
            error = 3
            new_file_path =  os.path.join( script_path,  new_name + ".py")
            error = 4
            val = os.makedirs(script_path, exist_ok=True)
            error = 5
                       
            #No creation or mode error with 'makedirs'.
            GSG_OT_ScriptRunner.runIt(file_path, new_name, new_file_path, cache_path)
        
        
        except OSError as exception:
            #errno.EEXIST = 17
            if exception.errno != errno.EEXIST:
                msg = "ScriptRunner error in 'checkDir': "
                print(msg, str(error) + ",  sysError: " + str(exception.errno) )
                
            else:
                #Shouldn't get here, but could with directory exists with mode error?
                GSG_OT_ScriptRunner.runIt(file_path, new_name, new_file_path, cache_path)    
                
                
        return
       

    def runIt(file_path, new_name, new_file_path, cache_path):
    
        try:
            error = 0
            
            #Allow seamless 'addon' usage by replacing '__main__' with the modules temp name.
            f = open(GSG_OT_ScriptRunner.check_escape_string(file_path), encoding="utf8")
            lines = f.readlines()
            f.close()
            
            found = False
            for each in lines:
                if each.find("__main__"):
                    found = True
                    break
                    
            if  found:
                f = open(GSG_OT_ScriptRunner.check_escape_string(new_file_path),'w')
                for each in lines:
                    line = each.replace("__main__", new_name)
                    f.writelines(line)
                f.close()
                 
            else:
                shutil.copy(file_path, new_file_path)
            
            
            error = 1
            bpy.utils.load_scripts(refresh_scripts = True)
            error = 2
            file_name = PathLeaf(file_path) 
            error = 3
            
            # print("\n")
            importlib.import_module(new_name)                
            
            print("\n" + "Script Runner - running file: " + '"' + file_name + '"' + "......Success!")
            
            GSG_OT_ScriptRunner.cleanUp(new_name, new_file_path, cache_path)            
             
        except:
          
            if error == 3:
                user_settings = GetUserPreferences()
                
                if user_settings.error_msg_verbose:
                    msg = "\n" + "Script Runner - script error in file: " + '"' + file_name + '"'
                    print(msg)
                    
                    formatted_lines = traceback.format_exc().splitlines()
                    for each in formatted_lines:
                        #Ignore the errors created by 'Script Runner'.
                        if each.find("frozen importlib") == -1:
                            if each.find(new_file_path) != -1:
                                each = each.replace(new_file_path, file_path)
                                
                            print(each)
                    
                else:
                    msg = "\n" + "Script Runner - script error in file: " + '"' + file_name + '"  '
                    formatted_lines = traceback.format_exc().splitlines()
                                       
                    for i in range(len(formatted_lines) - 4, len(formatted_lines)):
                        if formatted_lines[i].find(new_file_path) != -1:
                            formatted_lines[i] = formatted_lines[i].replace(new_file_path, file_path)
                        
                        pos = formatted_lines[i].rfind('line ')
                        if pos != -1:
                            line_num = formatted_lines[i][pos::]
          
                     
                    print(msg + line_num)
                    print(formatted_lines[-3])
                    print(formatted_lines[-2])
                    print(formatted_lines[-1])    
                                      
            else:
                msg = "Script Runner error in 'runIt': "
                print(msg, error)       
            
            
            GSG_OT_ScriptRunner.cleanUp(new_name, new_file_path, cache_path)    
        
        return


    def check_escape_string(s):
        backslash_map = { '\a': r'\a', '\b': r'\b', '\f': r'\f', '\n': r'\n', '\r': r'\r', '\t': r'\t', '\v': r'\v' }
        for key, value in backslash_map.items():
            s = s.replace(key, value)
        return s
        
        
    def cleanUp(new_name, new_file_path, cache_path):
        try:
            error = 4
            #Clean up the files.
            os.remove(new_file_path)
            error = 5
            #print(ScriptRunner.findFile(new_name + ".*", cache_path))                        
            cache_file = GSG_OT_ScriptRunner.findFile(new_name + ".*", cache_path)[0]
            error = 6
            os.remove(cache_file)   
        
        except:
            #If import fails then there is no 'cache_file' to clean up so error 4 gets reported.
            if error != 5:
                msg = "ScriptRunner error in 'cleanUp':  "
                print(msg, error)   
        
        
        return
        
           
    def findFile(pattern, path):
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result
    
    
    
    
    
#--Script buttons  


class GSG_OT_DirectoryLoad(bpy.types.Operator, ImportHelper):
    bl_idname = "object.load_directory"
    bl_label = "Load Scripts"
    bl_description = "Load all Scripts from a Directory"

    
    filter_glob = StringProperty(
        default="*.py",
        options={'HIDDEN'},
        )

    filename_ext = ".py";


    def execute(self, context):
        # print (self.filepath)
        if (self.filepath == ""):
            pass
        else:
            #Check if file exists, could be a path.
            if os.path.isfile(self.filepath):
                head, tail = ntpath.split(self.filepath)
                files = GSG_OT_ScriptRunner.findFile("*.py", head)
                # print(files)
                
                user_settings = GetUserPreferences()
                loaded_scripts = 0
                
                # Step through the files.
                for file in files:
                    # Step through the slots looking for an empty place to load the path.
                    for script_slot in range(0, gl_num_slots): 
                        if user_settings.script_paths[script_slot] == "":
                            user_settings.script_paths[script_slot] = file
                            break
                
                SaveSlots()
                # Pop-up dir window doesn't trigger a redraw to Blender's main interface.
                #   Thus, paths don't appear on buttons right away.
                RedrawAllWindows()
            
        return {'FINISHED'}


        
class GSG_OT_SlotsClear(bpy.types.Operator):
    bl_idname = "object.clear_slots"
    bl_label = "Clear Slots"
    bl_description = "Clear all Slots"

    
    def execute(self, context):
        for script_slot in range(0, gl_num_slots): 
            ClearSlot(script_slot)
        
        SaveSlots()
        
        return {'FINISHED'}            
        
  

class GSG_OT_ScriptLoad(bpy.types.Operator, ImportHelper):
    bl_idname = "object.script_load"
    bl_label = "Load Script"
    bl_description = "Assign a script to this slot"

    
    script_slot = IntProperty()
            
    filter_glob = StringProperty(
        default="*.py",
        options={'HIDDEN'},
        )

    filename_ext = ".py";


    def execute(self, context):
                
        if (self.filepath == ""):
            pass
        else:
            #Check if file exists, could be a path.
            if os.path.isfile(self.filepath):
                user_settings = GetUserPreferences()
                user_settings.script_paths[self.script_slot - 1] = self.filepath
                
                SaveSlots()
                
                
        return {'FINISHED'}


        
class GSG_OT_ScriptClear(bpy.types.Operator):
    bl_idname = "object.script_clear"
    bl_label = "Clear Script"
    bl_description = "Clear the script from this slot"


    script_slot = IntProperty()
    
    
    def execute(self, context):
        ClearSlot(self.script_slot)
        SaveSlots()
        
        return {'FINISHED'}            



class GSG_OT_ScriptRun(bpy.types.Operator):
    bl_idname = "object.script_run"
    bl_label = "Run Script"
    bl_description = "Run the script in this slot"

    script_slot = IntProperty()
    
    
    def execute(self, context):
        user_settings = GetUserPreferences()
        
        # print ("slot ", self.script_slot + 1)
        file_path = user_settings.script_paths[self.script_slot]
        
        if os.path.isfile(file_path):
            GSG_OT_ScriptRunner.checkDir(file_path)
        else:
            ClearSlot(self.script_slot)    
            
        return {'FINISHED'}



    

#------------------------Functions
   
def ClearSlot(script_slot):
    
    user_settings = GetUserPreferences()
    user_settings.script_paths[script_slot] = ""
    
    return
   
 
 
#If the file ends with a slash, the basename will be empty.
def PathLeaf(path):
    head, tail = ntpath.split(path)
    
    return tail or ntpath.basename(head)



#Stored paths in user prefs may no longer be valid.
def CheckFiles():
    user_settings = GetUserPreferences()
    
    path_num = 0    
    for pth in user_settings.script_paths:
        if not os.path.isfile(pth): user_settings.script_paths[path_num] = ""
        path_num += 1
 

def SaveSlots():
    user_settings   = GetUserPreferences()
    slot_paths      = []
    
    # Step through the slots.
    for script_slot in range(0, gl_num_slots): 
        slot_paths.append(user_settings.script_paths[script_slot])
    
    dir_path    = GetAddonDir() 
    file_name   = gl_path_data_file
    displayed   = user_settings.num_scripts
    file_data   = [displayed, slot_paths]
    
    DumpToFile(dir_path, file_name, file_data)

def RestoreSlots():
    global gl_paths_loaded
    
    user_settings = GetUserPreferences()
    
    dir_path    = GetAddonDir() 
    file_name   = gl_path_data_file
    
    # Check for file first.
    if not os.path.isfile(os.path.join(dir_path, file_name)):
        return
        
    file_data = LoadFromFile(dir_path, file_name)
    # print ('Stored Displayed Slots: ', file_data[0])
    displayed = min(gl_num_slots, file_data[0])
    user_settings.num_scripts = displayed
    # print ('Displayed Slots: ', displayed)
    
    path_data = file_data[1]
    # print ('Paths: ', path_data)
    
    # Trucate in case user changed the settings.
    if len(path_data) > gl_num_slots:
        path_data = path_data[0 : gl_num_slots]
    
    script_slot = 0
    for path in path_data:
        user_settings.script_paths[script_slot] = path
        script_slot += 1
    
    gl_paths_loaded = True
        
def DumpToFile(dir_path, file_name, file_data):
    
    try:
        if os.path.exists(dir_path):
            file_path = os.path.join(dir_path, file_name)
            
            f = open(file_path, 'wb')    # a is append, w is over-write. r is read only.
            #f.write(binary_data_string)    # Use this method with the 'exact' size test.
            
            # This method pickles and writes all at once, but doesn't let you check the size before writing.    
            pickle.dump(file_data, f, 1)    # Third argument '1' means binary.
            
            f.close()
            # print 'saved'
            return True
            
        
    except:
        formatted_lines = traceback.format_exc().splitlines()
        for each in formatted_lines:
            print(each)
        
        try:
            f.close()
        except:
            pass
            
        return False
   
def LoadFromFile(dir_path, file_name):            
    
    try:
        f = None
        file_path = os.path.join(dir_path, file_name)
        if os.path.isfile(file_path):
            f = open(file_path, 'rb')    # a is append, w is over-write. r is read only.
        
        if f:
            file_data = pickle.load(f)          # 411% faster than 'pickle' loading a data slot.
            #data = pickle.load(f)
            
            f.close()
            return file_data
        else:
            return None
            
    except:
        #A damaged file will throw an '.UnpicklingError'
        
        formatted_lines = traceback.format_exc().splitlines()
        for each in formatted_lines:
            print(each)
        
        try:
            f.close()
        except:
            pass
            
            
        return None

      
def GetAddonDir():
    # current_file gets the current path (including file) of the .blend or .py file executing if the script is running in the text editor.
    #If this script is running as an addon, then current_file returns a directory showing where the addon is installed.
    
    current_file = os.path.dirname(os.path.realpath(__file__)) 
    addon_dir = current_file + os.path.sep
    # print("Directory:", addon_dir)
    
    return addon_dir
        
        
def RedrawAllWindows():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()  
    

#----------------Register/Unregister

def CreateMenu(self, context):
   self.layout.operator(GSG_OT_ScriptRunner.bl_idname,text="GSG Script Runner - (.py)");

   

# This updates the class properties to annotation format for 2.8.   
def MakeAnnotations(cls):
    """Converts class fields to annotations if running with Blender 2.8"""
    if bpy.app.version < (2, 80):
        return cls
    bl_props = {k: v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls
    

    
# Register with a tuple, except for the panels which are displayed according to the user.
classes = (
    ScriptRunnerAddonPreferences,
    GSG_OT_ScriptRunner,
    GSG_OT_ScriptLoad,
    GSG_OT_ScriptClear,
    GSG_OT_ScriptRun,
    GSG_OT_DirectoryLoad,
    GSG_OT_SlotsClear,
)
   
   
if bpy.app.version >= (2, 80):
    
    def register():
        for cls in classes:
            cls = MakeAnnotations(cls)
            bpy.utils.register_class(cls)
        
        
        user_settings = GetUserPreferences()
        if user_settings.display_text_editor:
            bpy.utils.register_class(GSG_PT_script_runner_panel_1)
        
        if user_settings.display_3d:
            bpy.utils.register_class(GSG_PT_script_runner_panel_2)
        
        # print ("GSG reg ", hasattr(bpy.types, "GSG_PT_script_runner_panel_1"))
        
        # File import menu entry.
        bpy.types.TOPBAR_MT_file_import.append(CreateMenu);
        
        RestoreSlots()
        CheckFiles()
        
    
    def unregister():
        for cls in reversed(classes):
            cls = MakeAnnotations(cls)
            bpy.utils.unregister_class(cls)
        
        
        # Check if they exist per user settings.
        if hasattr(bpy.types, "GSG_PT_script_runner_panel_1"):
            bpy.utils.unregister_class(GSG_PT_script_runner_panel_1)
            
        if hasattr(bpy.types, "GSG_PT_script_runner_panel_2"):
            bpy.utils.unregister_class(GSG_PT_script_runner_panel_2)
        
        # print ("GSG unreg ", hasattr(bpy.types, "GSG_PT_script_runner_panel_2"))    
        
        # File import menu entry.
        bpy.types.TOPBAR_MT_file_import.remove(CreateMenu)
              
else:
    # Blender 2.79 and below.
    def register():
        bpy.utils.register_class(ScriptRunnerAddonPreferences)
        bpy.utils.register_class(GSG_OT_ScriptRunner)
        
        user_settings = GetUserPreferences()
        if user_settings.display_text_editor:
            bpy.utils.register_class(GSG_PT_script_runner_panel_1)
        
        if user_settings.display_3d:
            bpy.utils.register_class(GSG_PT_script_runner_panel_2)
            
            
        bpy.utils.register_class(GSG_OT_ScriptLoad)
        bpy.utils.register_class(GSG_OT_ScriptClear)
        bpy.utils.register_class(GSG_OT_ScriptRun)
        bpy.utils.register_class(GSG_OT_DirectoryLoad)
        bpy.utils.register_class(GSG_OT_SlotsClear)
        
        bpy.types.INFO_MT_file_import.append(CreateMenu);
        
        RestoreSlots()
        CheckFiles()
      
        
    def unregister():
        bpy.types.INFO_MT_file_import.remove(CreateMenu)    
        try:
            if bpy.types.GSG_PT_script_runner_panel_1 != None:
                bpy.utils.unregister_class(GSG_PT_script_runner_panel_1)    
        except:
            pass

        try:
            if bpy.types.GSG_PT_script_runner_panel_2 != None:
                bpy.utils.unregister_class(GSG_PT_script_runner_panel_2)    
        except:
            pass
        
            
        bpy.utils.unregister_class(GSG_OT_ScriptRunner)
        
        bpy.utils.unregister_class(GSG_OT_ScriptLoad)
        bpy.utils.unregister_class(GSG_OT_ScriptClear)
        bpy.utils.unregister_class(GSG_OT_ScriptRun)
        bpy.utils.unregister_class(GSG_OT_DirectoryLoad)
        bpy.utils.unregister_class(GSG_OT_SlotsClear)
        
        
        
        bpy.utils.unregister_class(ScriptRunnerAddonPreferences) 
 
 
           
if (__name__ == "__main__"):
   register();
       
       
       
       
       
       
       
       
       
       
   