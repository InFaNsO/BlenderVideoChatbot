import bpy
import json

class VideoEditorPanel(bpy.types.Panel):
    bl_label = "Video Editor"
    bl_idname = "OBJECT_PT_Video_Editor"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Gemini"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("object.videoinsert", text="Insert Visuals")