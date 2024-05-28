import bpy
import requests
import json
import re

from .GeminiChatOperator import url, header, d, GetData

scriptFormat = {
    "title": "title",
    "script": [
        {
            "speaker": "Narrator",
            "time_start": 0,
            "duration": 0,
            "text": "Dialouge that the speaker says",
            "shots_description": [
                {
                    "duration": 1,
                    "description": "visual details for the duration of this shot"
                },
                {
                    "duration": 4,
                    "description": "visual details for the duration of this shot"
                }
            ]
        }
    ]
}

formatInitial = {
    "title": "title",
    "title_key": "Search Key Words for the title",
    "script": [
        {
            "speaker": "Narrator",
            "text": "Dialouge that the speaker says",
        }
    ]
}

shotsFormat = {
    "shots_description": [
        {
            "duration": 1.3,
            "description": "Visual details for the shot",
            "key_words": "Search Key Words for the description"
        },
        {
            "duration": 2.6,
            "description": "Visual details for another the shot",
            "key_words": "Search Key Words for the description"
        }
    ]
}

chat_data = d

def fix_json_quotes(json_str):
    # Replace single quotes around property names and values, but not within words
    # Match single quotes that are preceded or followed by a non-word character or the start/end of the string
    json_str = re.sub(r'(?<!\\)(\b\'|\'\b)', '"', json_str)
    print(json_str)
    print('\n\n')
    pat = "'},"
    rep = '"},'
    json_str = re.sub(pat, rep, json_str)
    print(json_str)
    return json_str

class GenerateBaseScriptOperator(bpy.types.Operator):
    bl_idname = "object.generatebasescript"
    bl_label = "GenerateBaseScript"

    useChatHistory = bpy.props.BoolProperty(name="UseChatHistory")  #type: ignore

    def execute(self, context):
        title = context.scene.title_input
        duration = context.scene.total_video_duration

        global formatInitial

        prompt  = f"You are a script writer for a promiment YouTube channel. You have to write a script for your next video which is about {title}, and should be {duration} seconds long. "
        prompt += f"You have to make sure the script uses elements of suspense, suprise, and feels rewarding for the viewer. "
        prompt += f"The script should use severel hooks connecting different scenes to keep the audience engaged. "
        prompt += f"YOUR response should strictly follow the given JSON format.\n{json.dumps(formatInitial)}\n"
        prompt += "in your json response the property should be in double quotes and not in single quote"

        chat = None
        if self.useChatHistory:
            chat = json.loads(context.scene.get("ChatHistory"))
        else:
            chat = chat_data

        #global chat
        chat["contents"].append(GetData(prompt, "user"))

        response = requests.post(url=url, headers=header, data=json.dumps(chat))

        if response.status_code == 200:
            print("Request Sucessfull!!")
            print("Complete Response: \n", response.json())
            print("\n")
            print("Response Body: \n", response.json()["candidates"][0]["content"]["parts"][0]["text"])
            chat["contents"].append(GetData(response.json()["candidates"][0]["content"]["parts"][0]["text"], "model"))
        else:
            print("Request failed with status code:", response.status_code)
            print("Response body:", response.text)

        s_script = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        

        context.scene["VideoGenerationChatHistory"] = s_script
        print(context.scene["VideoGenerationChatHistory"])
        print("\n\n")
        sc = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))
        print(sc)

        return {'FINISHED'}



shot_chat = d
shot_chat_scene = -1

class GenerateShotsForSceneOperator(bpy.types.Operator):
    bl_idname = "object.generateshotsforscene"
    bl_label = "GenerateShotForScene"

    sceneIndex: bpy.props.IntProperty(name = "Index For scene")     # type: ignore

    def SetGlobalVar(self):
        global shot_chat
        global shot_chat_scene

        if shot_chat_scene != self.sceneIndex:
            shot_chat = d
            shot_chat_scene = self.sceneIndex

    def SetShotDurations(self, scene , shots):
        finalDuration = scene["duration"]
        shotsDuration = 0.0

        for shot in shots:
            shotsDuration += shot["duration"]

        if shotsDuration == finalDuration:
            print("Shots are of correct length")
            return shots
        
        if shotsDuration > finalDuration:
            print(f"Shots are longer- shot dur: {shotsDuration} scene dur: {finalDuration}")
            diff = (shotsDuration - finalDuration) / len(shots)
            for shot in shots:
                shot["duration"] -= diff
        else:
            print(f"Shots are shorter- shot dur: {shotsDuration} scene dur: {finalDuration}")
            diff = (finalDuration - shotsDuration) / len(shots)
            for shot in shots:
                shot["duration"] += diff

        return shots

    def execute(self, context):
        self.SetGlobalVar()

        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))
        speech = script["script"][self.sceneIndex]["text"]

        print("Generating Shots for speech: ", speech, "\n\n")

        prompt  = "You are a Video Producer for a famous YouTube Channel. Currently you are working on a video titled: " + script["title"] + ". "
        prompt += "You have to suggest what all shots would go in it's scene "+ str(self.sceneIndex) + " which is " + str(script["script"][self.sceneIndex]["duration"]) + " seconds long."
        prompt += "In the scene narrator is saying-\n" + speech + "\n"
        prompt += "Your Response should strictly be in the following json format:\n" + json.dumps(shotsFormat)
        prompt += "YOU HAVE TO MAKE SURE THAT in your json response the property should be in double quotes and not in single quote"
        
        print("prompt: ", prompt)

        global shot_chat
        shot_chat["contents"].append(GetData(prompt, "User"))

        response = requests.post(url=url, headers=header, data=json.dumps(shot_chat))

        if response.status_code != 200:
            print(f"Error in synthing speech: {response.status_code} - {response.text}")
            return {'FINISHED'}
        
        s_reply = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(f"{response.json()}\n\n{s_reply}")

        desc = json.loads(s_reply)
        s_reply = json.dumps(desc["shots_description"])

        reply = json.loads(s_reply)
        reply = self.SetShotDurations(script["script"][self.sceneIndex], reply)
        script["script"][self.sceneIndex]["shots_description"] = reply

        s_json = json.dumps(script)
        context.scene["VideoGenerationChatHistory"] = s_json
        print(s_json)

        return {'FINISHED'}




class VideoGenerationOperator(bpy.types.Operator):
    bl_idname = "object.videogeneration"
    bl_label = "VideoGeneration"

    firstTime = True

    def execute(self, context):
        title = context.scene.title_input
        duration = context.scene.total_video_duration

        global scriptFormat

        prompt = f"You Have to write a {duration} second script on the topic {title}. Your response should only be in the following json format\n"
        prompt += json.dumps(scriptFormat) + "\n"
        prompt += f"Make sure the sum of individual shot duration equals to the the total duration of the element.\n"
        prompt += f"Also, Make sure the time start for the element is equal to the previous element time start + duration.\n"
        prompt += f"THIS IS VERY IMPORTANT \n You have to make sure that each shot in shots_description should only include 1 visual element. If you have to make a montage of  clips split it into multiple shots with smaller duration"


        chat["contents"].append(GetData(prompt, "user"))


        response = requests.post(url=url, headers=header, data=json.dumps(chat))

        if response.status_code == 200:
            print("Request Sucessfull!!")
            print("Response Body: \n", response.json()["candidates"][0]["content"]["parts"][0]["text"])
            chat["contents"].append(GetData(response.json()["candidates"][0]["content"]["parts"][0]["text"], "model"))
        else:
            print("Request failed with status code:", response.status_code)
            print("Response body:", response.text)

        context.scene["VideoGenerationChatHistory"] = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(context.scene["VideoGenerationChatHistory"])
        print("\n\n")
        sc = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))
        print(sc)



        return {'FINISHED'}