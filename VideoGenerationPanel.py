import bpy
import json

class VideoGeneratrionPanel(bpy.types.Panel):
    bl_label = "Video Generation"
    bl_idname = "OBJECT_PT_Video_Gen"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Gemini"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.prop(context.scene, "title_input", text="Title")
        layout.prop(context.scene, "total_video_duration", text="Duration")
        layout.operator("object.videogeneration", text="Generate Video")


        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))

        if "title" in script:
            for element in script["script"]:
                outerBox = layout.box()
                col = outerBox.column()
                row = col.row()
                label = "Starting Time: " + str(element["time_start"]) 
                row.label(text=label)
                label = "Duration: " + str(element["duration"])
                row.label(text=label)
                label = element["speaker"] + ": " + element["text"]
                row = col.row()
                row.label(text=label)
                row = col.row()
                innerBox = row.box()
                inCol = innerBox.column()
                inRow = inCol.row()

                for shot in element["shots_description"]:
                    label = "" + str(shot["duration"]) + "sec: " + shot["description"]
                    inRow.label(text=label)
                    inRow = inCol.row()
                    




def register():
    bpy.types.Scene.title_input = bpy.props.StringProperty(name="title_input", description="title for the video to make")
    bpy.types.Scene.total_video_duration = bpy.props.IntProperty(name="total_video_duration", description="total duration of the video")

def unregister():
    del bpy.types.Scene.title_input
    del bpy.types.Scene.total_video_duration



