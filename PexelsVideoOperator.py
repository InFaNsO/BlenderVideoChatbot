import bpy
import json
import requests
from .LocalVariables import path 

apiKey = "uWby7NPaTxbZyq4jZZ7w28PjkNJnkheZlaGamaUfelvVEUiIRVKKipeF"

headers = {
    'Authorization': apiKey
}

params = {
    'query': "",
    'per_page': 3,
    'page': 1,
    'orientation': "landscape",
    'size': "medium"
}

url = "https://api.pexels.com/videos/search"

class PexelsVideoOperator(bpy.types.Operator):
    bl_idname = "object.pexelsvideo"
    bl_label = "PexelsVideoOperator"

    sceneIndex: bpy.props.IntProperty(name = "Index For scene")     # type: ignore
    shotIndex: bpy.props.IntProperty(name = "Index For shot")       # type: ignore

    def DownloadFile(self, downloadUrl, fileName):
        with requests.get(downloadUrl, stream=True) as response:
            response.raise_for_status()
            with open(fileName, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        return

    def execute(self, context):
        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))

        if "title" not in script:
            self.report({'WARNING'}, "Script Empty!")
            return {'FINISHED'}
        
        mainKey = ""
        if "title_key" in script:
            mainKey += script["title_key"]
        
        scene = script["script"][self.sceneIndex]
        shot = scene["shots_description"][self.shotIndex]

        global params
        params["query"] = shot["description"]

        response = requests.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            print("Response Pexels: \n")
            print(data)
            print("\nEnd Of response Pexels")
            videoObj = data["videos"][0]["video_files"][0]
            
            format = videoObj["file_type"].split("/")
            videoURL = videoObj["link"]
            
            p = path + "Scene " + str(self.sceneIndex) + " Shot " + str(self.shotIndex) + "." + format[-1] 
            print("\n" + p + "\n")
            self.DownloadFile(downloadUrl=videoURL, fileName=p)

            script["script"][self.sceneIndex]["shots_description"][self.shotIndex]["video"] = p
            s_json = json.dumps(script)
            context.scene["VideoGenerationChatHistory"] = s_json
            print(json.loads(context.scene.get("VideoGenerationChatHistory")))

        else:
            print(f"Request failed with status code {response.status_code}")
            print(response.text)

        return {'FINISHED'}
