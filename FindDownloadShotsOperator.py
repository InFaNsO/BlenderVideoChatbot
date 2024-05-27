import bpy
import json
import requests
import copy

from .PexelsVideoOperator import headers, params, url, path

def GetPexelResponse(search, perPage=3, querryUrl=url, page=1, orientation="landscape", size="medium"):
    params["query"] = search
    params["per_page"] = perPage
    params["page"] = page
    params["orientation"] = orientation
    params["size"] = size
    response = requests.get(url=querryUrl, headers=headers, params=params)
    return response

def FindSuitableVideo(response, startIndex = 0, prvUrls=[]):
        vidArray = response["videos"]
        for index, vidData in enumerate(vidArray[startIndex:], start=startIndex):
            for vidFile in vidData["video_files"]:
                if vidFile["quality"] == "hd" or vidFile["quality"] == "uhd":
                    foundUrl = False
                    for url in prvUrls:
                        if url == vidFile["link"]:
                            foundUrl = True
                            break

                    if foundUrl:
                        continue
                    print("Found Video in video number: " + str(index))
                    obj = videoObj
                    obj["url"] = vidFile["link"]
                    obj["page_no"] = response["page"]
                    obj["page_index"] = index
                    obj["per_page"] = response["per_page"]
                    obj["file_type"] = vidFile["file_type"]
                    return obj
        return None


videoObj = {
    "path": "",
    "url": "",
    "page_no": 0,
    "page_index": -1,
    "per_page": 0,
    "file_type":""
}

class FindDownloadShotsOperator(bpy.types.Operator):
    bl_idname = "object.finddownloadshots"
    bl_label = "FindInsertShots"

    def execute(self, context):
        #Get The Script from scene
        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))

        if "title" not in script:
            self.report({'WARNING'}, "Script Empty!")
            return {'FINISHED'}

        #clear the directory for use
        #delete_contents_of_folder(path)

        #loop through all scenes and their shots
        videoLinks = []

        for indexScene, scene in enumerate(script["script"]):
                shots = scene["shots_description"]
                for indexShot, shot in enumerate(shots):
                    print("Finding Videos for Scene: " + str(indexScene) + " Shot: " + str(indexShot) + "\nDescription: " + shot["description"])
                    
                    #Download the file now
                    mainKey = ""
                    if "title_key" in script:
                        mainKey += script["title_key"]
                    #the first querry
                    pexelResponse = GetPexelResponse(mainKey + shot["key_words"] + shot["description"])

                    if pexelResponse.status_code == 200:
                        responseData = pexelResponse.json()

                        #find most suitable video
                        downloadVideoObj = FindSuitableVideo(responseData, prvUrls=videoLinks)
                        #keep searching until one is found
                        while downloadVideoObj == None:
                            print("Could not find suitable video in page: " + str(responseData["page"]) + "\nQuerry: " + shot["description"])
                            pexelResponse = GetPexelResponse(shot["description"], page=responseData["page"] + 1)
                            if pexelResponse.status_code == 200:
                                responseData = pexelResponse.json()
                                downloadVideoObj = FindSuitableVideo(responseData, prvUrls=videoLinks)
                            else:
                                print(f"Request failed with status code {pexelResponse.status_code}")
                                print("Failed to find Videos for Scene: " + str(indexScene) + " Shot: " + str(indexShot) + "Page: " + str(responseData["page"]))
                                print(pexelResponse)
                                break
                        
                        videoLinks.append(downloadVideoObj["url"])
                        path = DownloadFile(downloadVideoObj, sceneIndex=indexScene, shotIndex=indexShot, query=mainKey + shot["key_words"])
                        downloadVideoObj["path"] = path
                        print(json.dumps(downloadVideoObj))
                        script["script"][indexScene]["shots_description"][indexShot]["video"] = copy.deepcopy(downloadVideoObj)

                        print(json.dumps(script["script"][indexScene]))

                    else:
                        print(f"Request failed with status code {pexelResponse.status_code}")
                        print("Failed to find Videos for Scene: " + str(indexScene) + " Shot: " + str(indexShot))
                        print(pexelResponse)   

        print(json.dumps(script["script"][indexScene]))

        dump_json = json.dumps(script)
        context.scene["VideoGenerationChatHistory"] = dump_json      
        return {'FINISHED'}
    


class ReplaceVideoOperator(bpy.types.Operator):
    bl_idname = "object.replacevideo"
    bl_label = "ReplaceVideo"

    sceneIndex: bpy.props.IntProperty(name = "Index For scene")     # type: ignore
    shotIndex: bpy.props.IntProperty(name = "Index For shot")       # type: ignore

    def execute(self, context):

        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))
        print(context.scene.get("VideoGenerationChatHistory", "{}"))

        if "title" not in script:
            self.report({'WARNING'}, "Script Empty!")
            return {'FINISHED'}
        
        videoLinks = []
        for scene in script["script"]:
            for shot in scene["shots_description"]:
                videoLinks.append(shot["video"]["link"])

        shot = script["script"][self.sceneIndex]["shots_description"][self.shotIndex]
        path = shot["video"]["path"]

        #delete the old file
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Error when deleating file: {e}")

        vid_object = shot["video"]
        #Search again for a video
        mainKey = ""
        if "title_key" in script:
            mainKey += script["title_key"]
        pexelResponse = GetPexelResponse(search=mainKey + shot["key_words"] + shot["description"], perPage=vid_object["per_page"], page=vid_object["page_no"])

        if pexelResponse.status_code != 200:
            print(f"Request failed with status code {pexelResponse.status_code}  {pexelResponse.text}")
            print("Failed to find Videos for Scene: " + str(self.sceneIndex) + " Shot: " + str(self.shotIndex))
            return {"FINISHED"}
        
        responseData = pexelResponse.json()

        #find most suitable video
        downloadVideoObj = FindSuitableVideo(responseData, vid_object["page_index"] + 1, prvUrls=videoLinks)
        #keep searching until one is found
        while downloadVideoObj == None:
            print("Could not find suitable video in page: " + str(responseData["page"]) + "\nQuerry: " + shot["description"])
            pexelResponse = GetPexelResponse(search=mainKey + shot["key_words"] + shot["description"], page=responseData["page"] + 1)
            if pexelResponse.status_code == 200:
                responseData = pexelResponse.json()
                downloadVideoObj = FindSuitableVideo(responseData, prvUrls=videoLinks)
            else:
                print(f"Request failed with status code {pexelResponse.status_code}")
                print("Failed to find Videos for Scene: " + str(self.sceneIndex) + " Shot: " + str(self.shotIndex) + "Page: " + str(responseData["page"]))
                print(pexelResponse)
                break
        
        print("\nOld URL: " + shot["video"]["url"])
        print("\nNew URL: " + downloadVideoObj["url"])

        #Find the strip in which to replace
        stripName = f"Scene {self.sceneIndex} Shot {self.shotIndex}" 
        strip = None
        sequence_editor = bpy.context.scene.sequence_editor_create()

        for strp in sequence_editor.sequences:
            if stripName == strp.name:
                strip = strp
                break

        if strip == None:
            self.report({'WARNING'}, "Strip not found!")
            return {'FINISHED'}
        elif strip.type != "MOVIE":
            self.report({'WARNING'}, "Strip Type not video")
            return {'FINISHED'}

        insertFrame = strip.frame_start
        end_frame = strip.frame_final_duration
        sequence_editor.sequences.remove(strip)

        #Download the file now
        downloadVideoObj["path"] = DownloadFile(downloadVideoObj, sceneIndex=self.sceneIndex, shotIndex=self.shotIndex, query=mainKey + shot["key_words"])
        
        strip = sequence_editor.sequences.new_movie(name=stripName, filepath=downloadVideoObj["path"], channel=7, frame_start=int(insertFrame), fit_method='FILL')
        strip.frame_final_duration = int(end_frame)
        strip.channel = 3

        #Update the entry for it
        script["script"][self.sceneIndex]["shots_description"][self.shotIndex]["video"] = copy.deepcopy(downloadVideoObj)
        dump_json = json.dumps(script)
        context.scene["VideoGenerationChatHistory"] = dump_json 

        return {'FINISHED'}


def DownloadFile(videoDOwnloadObj, sceneIndex, shotIndex, query):
    format = videoDOwnloadObj["file_type"].split("/")
    vUrl = videoDOwnloadObj["url"]
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