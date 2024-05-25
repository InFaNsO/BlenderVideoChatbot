import bpy
import requests
import json
import base64
from .GeminiChatOperator import key, header
from .PexelsVideoOperator import path

synth_url = f"https://texttospeech.googleapis.com/v1beta1/text:synthesize?key={key}"


voiceName = "en-US-Journey-F"

param = {
    "input": {
        "text": "Hey Im BG's AI app"
    },
    "voice": {
        "name": voiceName,
        "languageCode": "en-US"
    },
    "audioConfig": {
        "audioEncoding": "MP3"
    }
}

'''
bpy.ops.sequencer.sound_strip_add(
    filepath="C:\\Users\\Bhavil\\Desktop\\Codes\\ChatBotAddOn\\BlenderVideoChatbot\\downloads\\Scene 0.mp3", 
    directory="C:\\Users\\Bhavil\\Desktop\\Codes\\ChatBotAddOn\\BlenderVideoChatbot\\downloads\\", 
    files=[{"name":"Scene 0.mp3", "name":"Scene 0.mp3"}], frame_start=4, channel=3, overlap_shuffle_override=True)

'''

def frameToSec(frame):
    fps = float(bpy.context.scene.render.fps)    
    return float(frame) / fps

class AudioGeneratorOperator(bpy.types.Operator):
    bl_idname = "object.audiogenerator"
    bl_label = "AudioGenerator"

    def execute(self, context):
        #Get The Script from scene
        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))

        if "title" not in script:
            self.report({'WARNING'}, "Script Empty!")
            return {'FINISHED'}

        print(script)

        for indexScene, scene in enumerate(script["script"]):
            param["input"]["text"] = scene["text"]
            response = requests.post(url=synth_url, headers=header, json=param)
            
            if response.status_code != 200:
                print(f"Error in synthing speech: {response.status_code} - {response.text}")
            
            responseObj = response.json()

            audioData = base64.b64decode(responseObj["audioContent"])

            outputFile = path + "Scene " + str(indexScene) + ".mp3"
            with open(outputFile, "wb") as file:
                file.write(audioData)
            
            script["script"][indexScene]["audio"] = outputFile

        s_json = json.dumps(script)
        context.scene["VideoGenerationChatHistory"] = s_json
        print("\n\n",s_json)

        return {'FINISHED'}


class InsertAudioOperator(bpy.types.Operator):
    bl_idname = "object.insertaudio"
    bl_label = "InsertAudio"

    def execute(self, context):
        #Get The Script from scene
        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))

        if "title" not in script:
            self.report({'WARNING'}, "Script Empty!")
            return {'FINISHED'}
        
        sequence_editor = bpy.context.scene.sequence_editor_create()

        insertFrame = 0
        for indexScene, scene in enumerate(script["script"]):
            if "audio" not in scene:
                print(f"Audio File Not Present in Scene: {indexScene}" )
                return {'FINISHED'}
            
            #insert audio strip
            sound_strip = sequence_editor.sequences.new_sound(name=f"Scene {indexScene}", filepath=scene["audio"], channel=1, frame_start=insertFrame)
            
            #set the variables in script
            
            script["script"][indexScene]["time_start"] = frameToSec(insertFrame)

            duration_sec = frameToSec(sound_strip.frame_final_duration)
            script["script"][indexScene]["duration"] = duration_sec
            
            #set the insert frame for next scene
            insertFrame += sound_strip.frame_final_duration

        s_json = json.dumps(script)
        context.scene["VideoGenerationChatHistory"] = s_json
        print("\n\n",s_json)

        bpy.context.scene.frame_end = insertFrame

        return {'FINISHED'}
