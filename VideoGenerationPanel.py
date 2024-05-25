import bpy
import json

class VideoGeneratrionPanel(bpy.types.Panel):
    bl_label = "Video Generation"
    bl_idname = "OBJECT_PT_Video_Gen"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Gemini"

    def DoesAudioExists(self, context):
        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))
        if "title" not in script:
            return False
        
        for scene in script["script"]:
            if "audio" not in scene:
                return False

        return True
    
    def DoesScriptExists(self, context):
        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))
        if "title" not in script:
            return False
        return True

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.prop(context.scene, "title_input", text="Title")
        layout.prop(context.scene, "total_video_duration", text="Duration")
        r = layout.row()
        #check if audio exists
        if self.DoesAudioExists(context=context):
            r.operator("object.insertaudio", text="Insert Audio")
        else:
            r.operator("object.audiogenerator", text="Generate Audio")
    
        if not self.DoesScriptExists(context=context):
            r.operator("object.generatebasescript", text="Generate Base Script")
        else:
            r.label(text="Basic Script Generated")

        if not self.DoesScriptExists(context):
            return
        
        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))

        for sceneIndex, element in enumerate(script["script"]):
            outerBox = layout.box()
            col = outerBox.column()
            row = col.row()
            
            #First Line
            row.label(text=f"Scene {sceneIndex}")

            if "time_start" in element:
                row.label(text="Start Time: " + str(element["time_start"]))
            
            if "duration" in element:
                row.label(text="Duration: " + str(element["duration"]))

            #Second Line
            row = col.row()
            row.label(text="" + (element["speaker"]) + ":" + element["text"])

            if "shots_description" not in element:
                row = col.row()
                op = row.operator("object.generateshotsforscene", text="Generate Shots")
                op.sceneIndex = sceneIndex
                continue

            row = col.row()
            for shotIndex, shot in enumerate(element["shots_description"]):
                shotBox = row.box()
                shotCol = shotBox.column()
                shotRow = shotCol.row()

                shotRow.label(text="Shot " + str(shotIndex))
                shotRow.label(text="Duration " + str(shot["duration"]))
                shotRow = shotCol.row()
                shotRow.label(text="Description: " + shot["description"])
                shotRow = shotCol.row()
                shotRow.label(text="Key Words: " + shot["key_words"])

                shotRow = shotCol.row()
                shotRow.label(text="Edit Shot")
                if "video" in shot:
                    op = shotRow.operator("object.videoinsert", text="Insert Visual")
                    op.sceneIndex = sceneIndex
                    op.shotIndex = shotIndex
                else:
                    ops = shotRow.operator("object.pexelsvideo", text="Find Visuals")
                    ops.sceneIndex = sceneIndex
                    ops.shotIndex = shotIndex
                row = col.row()

        



        '''
        if "title" in script:
            for sceneIndex, element in enumerate(script["script"]):
                outerBox = layout.box()
                col = outerBox.column()
                row = col.row()
                label = "Scene " + str(sceneIndex)
                row.label(text=label)
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

                for shotIndex, shot in enumerate(element["shots_description"]):
                    label = "Shot " + str(shotIndex)
                    inRow.label(text=label)
                    inRow = inCol.row()
                    label = "" + str(shot["duration"]) + "sec: " + shot["description"]
                    inRow.label(text=label)
                    if "video" in shot:
                        op = inRow.operator("object.videoinsert", text="Insert Visual")
                        op.sceneIndex = sceneIndex
                        op.shotIndex = shotIndex    
                    else:
                        op = inRow.operator("object.pexelsvideo", text="Find Visuals")
                        op.sceneIndex = sceneIndex
                        op.shotIndex = shotIndex
                    inRow = inCol.row()
        '''
                    




def register():
    bpy.types.Scene.title_input = bpy.props.StringProperty(name="title_input", description="title for the video to make")
    bpy.types.Scene.total_video_duration = bpy.props.IntProperty(name="total_video_duration", description="total duration of the video")

def unregister():
    del bpy.types.Scene.title_input
    del bpy.types.Scene.total_video_duration



