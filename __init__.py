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
from .VideoGenerationOperator import VideoGenerationOperator, GenerateBaseScriptOperator, GenerateShotsForSceneOperator, GenerateBaseScriptFromChat, GenerateAllShotsForAllScenes
from .VideoEditorPanel import VideoEditorPanel
from .VideoInsertOperator import VideoInsertOperator, VideoInsertAllOperator
from .FindDownloadShotsOperator import FindDownloadShotsOperator, ReplaceVideoOperator
from .AudioGeneratorOperator import AudioGeneratorOperator, InsertAudioOperator
from .AudioGenerationWithTranscription import PrintElevelLabsVoicesOperator, GenerateAudioAndSubtitlesOperator, InsertAudioAndSubtitlesOperator

from .PexelsVideoOperator import PexelsVideoOperator

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

    bpy.utils.register_class(GenerateBaseScriptOperator)
    bpy.utils.register_class(GenerateShotsForSceneOperator)
    bpy.utils.register_class(VideoGenerationOperator)
    bpy.utils.register_class(GenerateBaseScriptFromChat)
    bpy.utils.register_class(GenerateAllShotsForAllScenes)
    bpy.utils.register_class(VideoGeneratrionPanel)

    bpy.utils.register_class(VideoEditorPanel)
    bpy.utils.register_class(VideoInsertOperator)
    bpy.utils.register_class(VideoInsertAllOperator)
    bpy.utils.register_class(FindDownloadShotsOperator)
    bpy.utils.register_class(ReplaceVideoOperator)

    bpy.utils.register_class(AudioGeneratorOperator)
    bpy.utils.register_class(InsertAudioOperator)

    bpy.utils.register_class(PrintElevelLabsVoicesOperator)
    bpy.utils.register_class(GenerateAudioAndSubtitlesOperator)
    bpy.utils.register_class(InsertAudioAndSubtitlesOperator)

    
    bpy.utils.register_class(PexelsVideoOperator)

    # Register the property on the scene
    bpy.types.Scene.message_prop_ai = bpy.props.StringProperty(name="InputText")
    VideoGenerationPanel.register()

def unregister():
    bpy.utils.unregister_class(GeminiChatOperator)
    bpy.utils.unregister_class(GeminiChatPanel)
    
    bpy.utils.unregister_class(GenerateBaseScriptOperator)
    bpy.utils.unregister_class(GenerateShotsForSceneOperator)
    bpy.utils.unregister_class(VideoGenerationOperator)
    bpy.utils.unregister_class(GenerateBaseScriptFromChat)
    bpy.utils.unregister_class(GenerateAllShotsForAllScenes)
    bpy.utils.unregister_class(VideoGeneratrionPanel)

    bpy.utils.unregister_class(VideoEditorPanel)
    bpy.utils.unregister_class(VideoInsertOperator)
    bpy.utils.unregister_class(VideoInsertAllOperator)
    bpy.utils.unregister_class(FindDownloadShotsOperator)
    bpy.utils.unregister_class(ReplaceVideoOperator)

    bpy.utils.unregister_class(AudioGeneratorOperator)
    bpy.utils.unregister_class(InsertAudioOperator)

    bpy.utils.unregister_class(PrintElevelLabsVoicesOperator)
    bpy.utils.unregister_class(GenerateAudioAndSubtitlesOperator)
    bpy.utils.unregister_class(InsertAudioAndSubtitlesOperator)

    bpy.utils.unregister_class(PexelsVideoOperator)


    # UnRegister the property on the scene
    del bpy.types.Scene.message_prop_ai
    VideoGenerationPanel.unregister()


if __name__ == "__main__":
    register()
