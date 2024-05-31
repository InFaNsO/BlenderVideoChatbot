import bpy
import requests
import json
import base64
import copy
from .LocalVariables import path, eleven_labs_api_key
from .VideoGenerationPanel import DoesAudioExists


VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream/with-timestamps"

voicesUrl = "https://api.elevenlabs.io/v1/voices"

headers = {
  "Content-Type": "application/json",
  "xi-api-key": eleven_labs_api_key
}

data = {
  "text": "",
  "model_id": "eleven_multilingual_v2",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.75
  }
}

timeStampObj = {
    "word": "",
    "startTimeFrame": 0,
    "endTimeFrame": 0
}

transcriptionObj = {
    "narrator": "",
    "text" : "",
    "timeStamps": [
        timeStampObj
    ],
    "audio_file": ""
}

voices = {}

def frameToSec(frame):
    fps = float(bpy.context.scene.render.fps)    
    return float(frame) / fps

def SecToFrame(sec):
    fps = float(bpy.context.scene.render.fps)    
    return int(sec * fps)

def IsValidJson(text):
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False

def GetElevenLabResponse(textToSynth):
    data["text"] = textToSynth
    response = requests.post(url=url, json=data, headers=headers)

    if response.status_code != 200:
        print(f"Error encountered when generating speech for {textToSynth}\nStatus Code: {response.status_code}\nContent: {response.text}")
        return None

    json_string = response.content.decode("utf-8")
    obj_str = json_string.split("\n\n")
    response_dict = json.loads(obj_str[0])

    print(f"\n\n{json_string}\n")
    print(json.dumps(response_dict, indent=4))

    bytesArr = []

    for string in obj_str:
        if not IsValidJson(string):
            continue
        obj = json.loads(string)
        dataInBytes = obj["audio_base64"].encode('ascii')
        bytesDecoded = base64.decodebytes(dataInBytes)
        bytesArr.append(bytesDecoded)

    combinedData = bytesArr[0]
    for index, element in enumerate(bytesArr[1:], start=1):
        combinedData += element

    response_dict["audio_base64"] = base64.encodebytes(combinedData).decode('ascii')

    print(json.dumps(response_dict, indent=4))

    return response_dict


class PrintElevelLabsVoicesOperator(bpy.types.Operator):
    bl_idname = "object.printelevellabsvoices"
    bl_label = "PrintElevelLabsVoices"

    def execute(self, context):
        response = requests.get(voicesUrl, headers=headers)
        if response.status_code != 200:
            print(f"Error encountered when Getting voices\nStatus Code: {response.status_code}\nContent: {response.text}")
            return {'FINISHED'}
        
        global voices
        voices = json.loads(response.content.decode("utf-8"))
        print(json.dumps(voices))

        return {'FINISHED'}


class GenerateAudioAndSubtitlesOperator(bpy.types.Operator):
    bl_idname = "object.generateaudioandsubtitles"
    bl_label = "GenerateAudioAndSubtitles"

    def execute(self, context):

        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))

        if "title" not in script:
            self.report({'WARNING'}, "Script Empty!")
            return {'FINISHED'}
        
        for indexScene, scene in enumerate(script["script"]):
            print(scene["transcription"])
            scene["transcription"]["timeStamps"] = []
            transcriptionScene = scene["transcription"]

            print(f"Scene {indexScene}\n\n")
            print(json.dumps(scene, indent=4))
            print("\n\n")


            responseObj = None
            responseObj = GetElevenLabResponse(transcriptionScene["text"])                
            if responseObj == None:
                return

            audioData = base64.b64decode(responseObj["audio_base64"])
            outputFile = path + "Scene " + str(indexScene) + ".mp3"
            with open(outputFile, "wb") as file:
                file.write(audioData)
            
            transcriptionScene["audio_file"] = outputFile
            
            char_time_Stamps = responseObj["alignment"]
            charArr = char_time_Stamps["characters"]
            startTimeArr = char_time_Stamps["character_start_times_seconds"]
            endTimeArr = char_time_Stamps["character_end_times_seconds"]

            word = ""
            startCharIndex = -1
            endCharIndex = -1


            for index, c in enumerate(charArr):
                if startCharIndex == -1:
                    startCharIndex = index

                if c != ' ':
                    word += c
                    endCharIndex = index
                else:
                    obj = copy.deepcopy(timeStampObj)
                    obj["word"] = word
                    obj["startTimeFrame"] = SecToFrame(startTimeArr[startCharIndex])
                    obj["endTimeFrame"] = SecToFrame(endTimeArr[endCharIndex])

                    transcriptionScene["timeStamps"].append(obj)

                    word = ""
                    startCharIndex = -1
                    endCharIndex = -1

            if word != "":
                obj = copy.deepcopy(timeStampObj)
                obj["word"] = word
                obj["startTimeFrame"] = SecToFrame(startTimeArr[startCharIndex])
                obj["endTimeFrame"] = SecToFrame(endTimeArr[endCharIndex])
                transcriptionScene["timeStamps"].append(obj)

            print(scene["transcription"])
            script["script"][indexScene]["transcription"] = transcriptionScene

        s_json = json.dumps(script)
        context.scene["VideoGenerationChatHistory"] = s_json
        print("\n\n",s_json)

        return {'FINISHED'}


def InsertTextScene(sequence_editor, stripName, startFrame, endFrame, text, channel=9, fontSize = 30, location=[0.5,0.2], color=[1,1,1,1]):
    text_strip = sequence_editor.sequences.new_effect(name=stripName, type='TEXT', channel=channel, frame_start=startFrame, frame_end=endFrame)
    text_strip.text = text
    text_strip.font_size = fontSize
    text_strip.location = location
    text_strip.color = color
    text_strip.frame_final_duration = endFrame - startFrame
    return

class InsertAudioAndSubtitlesOperator(bpy.types.Operator):
    bl_idname = "object.insertaudioandsubtitles"
    bl_label = "InsertAudioAndSubtitles"

    def execute(self, context):
        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))

        if "title" not in script:
            self.report({'WARNING'}, "Script Empty!")
            return {'FINISHED'}
        
        if not DoesAudioExists(context=context):
            self.report({'WARNING'}, "Not All Scenes have Auidio files")
            return {'FINISHED'}
        
        print(json.dumps(script, indent=4))

        sequence_editor = bpy.context.scene.sequence_editor_create()
        insertFrame = 0

        wordsPerTime = 5

        for indexScene, scene in enumerate(script["script"]):

            ###Inser Audio File
            transcript = scene["transcription"]
            sound_strip = sequence_editor.sequences.new_sound(name=f"Scene {indexScene}", filepath=transcript["audio_file"], channel=1, frame_start=insertFrame)

            transcript["time_start_frame"] = insertFrame
            transcript["time_end_frame"] = sound_strip.frame_final_duration + insertFrame
            transcript["duration_frame"] = sound_strip.frame_final_duration

            insertFrame += transcript["duration_frame"]

            ###Inser Subtitles
            insertBuffer = int(sound_strip.frame_start)
            wordCounter = 0
            wordStr = ""
            wordStartFrame = -1
            wordEndFrame = -1

            for stamp in transcript["timeStamps"]:
                word = stamp["word"]
                startFrame = stamp["startTimeFrame"]
                endFrame = stamp["endTimeFrame"]
                if wordCounter == wordsPerTime:
                    #make the text screen
                    InsertTextScene(sequence_editor=sequence_editor, stripName=f"Text Scene {indexScene} - {wordStr}", startFrame=wordStartFrame+insertBuffer, endFrame=wordEndFrame+insertBuffer, text=wordStr)
                    wordCounter = 0
                    wordStr = ""
    
                    

                if wordCounter == 0:
                    wordStartFrame = startFrame

                wordStr += word + " "
                wordEndFrame = endFrame
                wordCounter += 1
            
            if wordCounter > 0:
                InsertTextScene(sequence_editor=sequence_editor, stripName=f"Text Scene {indexScene} - {wordStr}", startFrame=wordStartFrame+insertBuffer, endFrame=wordEndFrame+insertBuffer, text=wordStr)
                wordCounter = 0
            
            print(json.dumps(transcript, indent=4))
            script["script"][indexScene]["transcription"] = copy.deepcopy(transcript)


        s_json = json.dumps(script)
        context.scene["VideoGenerationChatHistory"] = s_json

        print("\n\n")
        print(json.dumps(script, indent=4))
        print("\n\n")

        bpy.context.scene.frame_end = insertFrame
        return {'FINISHED'}

