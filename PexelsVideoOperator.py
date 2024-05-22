import bpy
import json
import requests

apiKey = "uWby7NPaTxbZyq4jZZ7w28PjkNJnkheZlaGamaUfelvVEUiIRVKKipeF"

headers = {
    'Authorization': apiKey
}

params = {
    'query': "",
    'per_page': 1
}

url = "https://api.pexels.com/videos/search"

class PexelsVideoOperator(bpy.types.Operator):
    bl_idname = "object.pexelsvideo"
    bl_label = "PexelsVideoOperator"

    sceneIndex: bpy.props.IntProperty(name = "Index For scene")     # type: ignore
    shotIndex: bpy.props.IntProperty(name = "Index For shot")       # type: ignore

    def MakeURL(self, searchTerm):

        return f"{searchTerm}"
        

    def execute(self, context):
        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))

        if "title" not in script:
            self.report({'WARNING'}, "Script Empty!")
            return {'FINISHED'}
        
        scene = script["script"][self.sceneIndex]
        shot = scene["shots_description"][self.shotIndex]

        global params
        params["query"] = shot["description"]

        response = requests.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            print(data)
        else:
            print(f"Request failed with status code {response.status_code}")
            print(response.text)

        return {'FINISHED'}
