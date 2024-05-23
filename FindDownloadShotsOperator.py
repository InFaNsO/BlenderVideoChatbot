import bpy
import json
import requests

from .PexelsVideoOperator import headers, params, url, path

class FindDownloadShotsOperator(bpy.types.Operator):
    bl_idname = "object.finddownloadshots"
    bl_label = "FindInsertShots"

    def GetPexelResponse(self, search, perPage=3, querryUrl=url, page=1, orientation="landscape", size="medium"):
        params["query"] = search
        params["per_page"] = perPage
        params["page"] = page
        params["orientation"] = orientation
        params["size"] = size
        response = requests.get(url=querryUrl, headers=headers, params=params)
        return response
    
    def FindSuitableVideo(self, vidArray):
        for index, vidData in enumerate(vidArray):
            for vidFile in vidData["video_files"]:
                if vidFile["quality"] == "hd" or vidFile["quality"] == "uhd":
                    print("Found Video in video number: " + str(index))
                    return vidFile
        return None

    def execute(self, context):
        #Get The Script from scene
        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))

        if "title" not in script:
            self.report({'WARNING'}, "Script Empty!")
            return {'FINISHED'}

        #clear the directory for use
        delete_contents_of_folder(path)

        #loop through all scenes and their shots
        for indexScene, scene in enumerate(script["script"]):
                shots = scene["shots_description"]
                for indexShot, shot in enumerate(shots):
                    print("Finding Videos for Scene: " + str(indexScene) + " Shot: " + str(indexShot) + "\nDescription: " + shot["description"])
                    
                    #the first querry
                    pexelResponse = self.GetPexelResponse(shot["description"])

                    if pexelResponse.status_code == 200:
                        responseData = pexelResponse.json()

                        #find most suitable video
                        downloadVideoObj = self.FindSuitableVideo(responseData["videos"])
                        #keep searching until one is found
                        while downloadVideoObj == None:
                            print("Could not find suitable video in page: " + str(responseData["page"]) + "\nQuerry: " + shot["description"])
                            pexelResponse = self.GetPexelResponse(shot["description"], page=responseData["page"] + 1)
                            if pexelResponse.status_code == 200:
                                responseData = pexelResponse.json()
                                downloadVideoObj = self.FindSuitableVideo(responseData["videos"])
                            else:
                                print(f"Request failed with status code {pexelResponse.status_code}")
                                print("Failed to find Videos for Scene: " + str(indexScene) + " Shot: " + str(indexShot) + "Page: " + str(responseData["page"]))
                                print(pexelResponse)
                                break
                        
                        #Download the file now
                        nameFile = DownloadFile(downloadVideoObj, sceneIndex=indexScene, shotIndex=indexShot, query=shot["description"])
                        script["script"][indexScene]["shots_description"][indexShot]["video"] = nameFile
                    else:
                        print(f"Request failed with status code {pexelResponse.status_code}")
                        print("Failed to find Videos for Scene: " + str(indexScene) + " Shot: " + str(indexShot))
                        print(pexelResponse)   

        dump_json = json.dumps(script)
        context.scene["VideoGenerationChatHistory"] = dump_json      
        return {'FINISHED'}
    

def DownloadFile(videoDOwnloadObj, sceneIndex, shotIndex, query):
    format = videoDOwnloadObj["file_type"].split("/")
    vUrl = videoDOwnloadObj["link"]
    p = path + "Scene " + str(sceneIndex) + " Shot " + str(shotIndex) + " " + query + "." + format[-1]
    print("Downloading to: " + p)
    
    with requests.get(vUrl, stream=True) as response:
            response.raise_for_status()
            with open(p, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
    return p

import shutil
import os

def delete_contents_of_folder(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Delete the directory and its contents
        shutil.rmtree(folder_path)
        # Recreate the empty directory
        os.makedirs(folder_path)
        print(f"All contents of '{folder_path}' have been deleted.")
    else:
        print(f"The folder '{folder_path}' does not exist.")