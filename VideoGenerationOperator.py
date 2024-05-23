import bpy
import requests
import json

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

chat = d


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


        chat["contents"].append(GetData(self, prompt, "user"))


        response = requests.post(url=url, headers=header, data=json.dumps(chat))

        if response.status_code == 200:
            print("Request Sucessfull!!")
            print("Response Body: \n", response.json()["candidates"][0]["content"]["parts"][0]["text"])
            chat["contents"].append(GetData(self, response.json()["candidates"][0]["content"]["parts"][0]["text"], "model"))
        else:
            print("Request failed with status code:", response.status_code)
            print("Response body:", response.text)

        context.scene["VideoGenerationChatHistory"] = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        print(context.scene["VideoGenerationChatHistory"])
        print("\n\n")
        sc = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))
        print(sc)



        return {'FINISHED'}