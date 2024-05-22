# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "AIChatBot",
    "author" : "BG",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Custom"
}

import bpy
from .GeminiChatOperator import GeminiChatOperator 
from .GeminiChatPanel import GeminiChatPanel
from .VideoGenerationPanel import VideoGeneratrionPanel
from .VideoGenerationOperator import VideoGenerationOperator

class HelloWorldOperator(bpy.types.Operator):
    bl_idname = "object.hello_world_operator"
    bl_label = "Hello World Operator"

    def execute(self, context):
        self.report({'INFO'}, "Hello, World!")
        return {'FINISHED'}

class HelloWorldPanel(bpy.types.Panel):
    bl_label = "Hello World Panel"
    bl_idname = "OBJECT_PT_hello_world_panel"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Custom'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Hello, World!")
        layout.operator("object.hello_world_operator")




def register():
    bpy.utils.register_class(GeminiChatOperator)
    bpy.utils.register_class(GeminiChatPanel)
    bpy.utils.register_class(VideoGenerationOperator)
    bpy.utils.register_class(VideoGeneratrionPanel)
    # Register the property on the scene
    bpy.types.Scene.message_prop_ai = bpy.props.StringProperty(name="InputText")
    VideoGenerationPanel.register()

def unregister():
    bpy.utils.unregister_class(GeminiChatOperator)
    bpy.utils.unregister_class(GeminiChatPanel)
    bpy.utils.unregister_class(VideoGenerationOperator)
    bpy.utils.unregister_class(VideoGeneratrionPanel)
    # UnRegister the property on the scene
    del bpy.types.Scene.message_prop_ai
    VideoGenerationPanel.unregister()

if __name__ == "__main__":
    register()
