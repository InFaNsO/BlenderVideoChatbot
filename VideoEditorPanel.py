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

        
        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))

        if "title" not in script:
            layout.label(text="No Script In Scene")
            return
        
        if "shots_description" not in script["script"][0]:
             layout.label(text="No Shots in the scenes")


        allSceneHaveShot = True
        allShotsHavVideo = True
        for scene in script["script"]:
                if "shots_description" not in scene:
                     allSceneHaveShot = False
                     continue
                shots = scene["shots_description"]
                for shot in shots:
                     if "video" not in shot:
                        allShotsHavVideo = False
                        break
                     
        if allSceneHaveShot == False:
             layout.label(text="Not all Scenes have shots")
             return
        

        if allShotsHavVideo == False:
            layout.operator("object.finddownloadshots", text="Download All Shots")
        else:
            layout.operator("object.videoinsertall", text="Insert All Videos")

        return



