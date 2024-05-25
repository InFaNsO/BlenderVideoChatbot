import bpy
import json

'''
bpy.ops.sequencer.movie_strip_add(
    filepath="C:\\Users\\Bhavil\\Desktop\\Codes\\ChatBotAddOn\\BlenderVideoChatbot\\downloads\\Scene 2 Shot 0.mp4", 
    directory="C:\\Users\\Bhavil\\Desktop\\Codes\\ChatBotAddOn\\BlenderVideoChatbot\\downloads\\", 
    files=[{
        "name":"Scene 2 Shot 0.mp4", 
        "name":"Scene 2 Shot 0.mp4"
        }], 
    frame_start=0, channel=1, overlap_shuffle_override=True, fit_method='FIT', adjust_playback_rate=True)


bpy.ops.sequencer.split(frame=91, channel=2, type='SOFT', use_cursor_position=True, side='NO_CHANGE', ignore_selection=True)

'''

def SecToFrame(sec, frameRate=25):
    return sec * frameRate

class VideoInsertOperator(bpy.types.Operator):
    bl_idname = "object.videoinsert"
    bl_label = "VideoInsert"

    sceneIndex: bpy.props.IntProperty(name = "Index For scene")     # type: ignore
    shotIndex: bpy.props.IntProperty(name = "Index For shot")       # type: ignore

    insertAll: bpy.props.BoolProperty(name="Bool For Inseret")     # type: ignore

    def GetChannelNum(self, script):
        num = -1
        for indexScene, scene in enumerate(script["script"]):
            if indexScene <= int(self.sceneIndex):
                shots = scene["shots_description"]
                for indexShot, shot in enumerate(shots):
                    if indexShot == 0 or indexShot < int(self.shotIndex):
                        num += 2
            else:
                break

        return num

    def execute(self, context):
        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))

        #       code for specific shot to be added using the buttonm in UI

        scene = script["script"][self.sceneIndex]
        shot = scene["shots_description"][self.shotIndex]

        channelNum = self.GetChannelNum(script=script)
        
        print("Channel to insert in: " + str(channelNum))
        shotsDuration = 0

        for index, s in enumerate(scene["shots_description"]):
            if index < self.shotIndex:
                shotsDuration += s["duration"]
            else:
                break

        p = shot["video"].split('/')
        dir = ""
        for ele in p[:-1]:
            dir += ele + "/"

        startFrame = int(SecToFrame(sec=scene["time_start"]) + SecToFrame(sec=shotsDuration))
        print("Starting Frame: " + str(startFrame))

        InsertVideo(shot["video"], dir, startFrame)
        #bpy.ops.sequencer.movie_strip_add(filepath=shot["video"], directory=dir, files=[{"name":p[-1], "name":p[-1]}], frame_start=startFrame, channel=1, overlap_shuffle_override=False, fit_method='FILL', adjust_playback_rate=True)

        durationFrame = int(SecToFrame(sec=shot["duration"]))
        print(str(context.scene.sequence_editor.sequences_all))
        ReduceDuration(context, durationFrame, p[-1])


        #context.active_sequence_strip.frame_final_duration = durationFrame
        #bpy.ops.sequencer.split(frame=splitFrame, channel=channelNum, type="SOFT", side="RIGHT")
        #bpy.ops.sequencer.delete()

        '''
            THIS IS CODE FOR Adding all the videos in the script along with cutting them

        for scene in script["script"]:
            shots = scene["shots_description"]
            shotsDuration = 0
            for shot in shots:
                if "video" in shot:
                    #insert video at the correct time
                    p = shot["video"].split('/')
                    dir = ""
                    for ele in p[:-1]:
                        dir += ele + "/"

                    startFrame = int(bpy.utils.time_to_frame(scene["time_start"] + shotsDuration)) - 1

                    var = bpy.ops.sequencer.movie_strip_add(filepath=shot["video"], directory=dir, files=[{"name":p[-1], "name":p[-1]}], frame_start=startFrame, channel=channelNum, overlap_shuffle_override=True, fit_method='FILL', adjust_playback_rate=True)
                    print(var)

                    splitFrame = startFrame + int(bpy.utils.time_to_frame(shot["duration"])) - 1
                    bpy.ops.sequencer.split(frame=splitFrame, channel=channelNum, type="SOFT", side="RIGHT")
                    bpy.ops.sequencer.delete()
                    channelNum += 1
                    bpy.ops.sequencer.split(frame=splitFrame, channel=channelNum, type="SOFT", side="RIGHT")
                    bpy.ops.sequencer.delete()
                    channelNum +=1

                shotsDuration += shot["duration"]
        '''

        return {'FINISHED'}


def InsertVideo(filePath, dir, fram_start, channel=3):
        bpy.ops.sequencer.movie_strip_add(filepath=filePath, directory=dir, frame_start=fram_start, channel=channel, overlap_shuffle_override=False, fit_method='FILL', adjust_playback_rate=True, sound=False)
 
def ReduceDuration(context, endOfClipFrame, sequenseName):
    print(sequenseName)
    selected = context.active_sequence_strip
    print(str(selected))
    bpy.ops.sequencer.select_all(action='DESELECT')
    bpy.ops.sequencer.select(deselect_all=True)
    selected = context.active_sequence_strip
    print(str(selected))
    strip = context.scene.sequence_editor.sequences_all.get(sequenseName)
    print(str(strip))
    strip.frame_final_duration = endOfClipFrame

class VideoInsertAllOperator(bpy.types.Operator):
    bl_idname = "object.videoinsertall"
    bl_label = "VideoInsertAll"

    def execute(self, context):
        #Get The Script from scene
        script = json.loads(context.scene.get("VideoGenerationChatHistory", "{}"))

        if "title" not in script:
            self.report({'WARNING'}, "Script Empty!")
            return {'FINISHED'}
        
        sequence_editor = bpy.context.scene.sequence_editor_create()

        insertFrame = 0
        for indexScene, scene in enumerate(script["script"]):
                shots = scene["shots_description"]
                shotDuration = 0
                for indexShot, shot in enumerate(shots):
                    pathArr = shot["video"].split("/")
                    dir = ""
                    for ele in pathArr[:-1]:
                        dir += ele + "/"
                    
                    vid_clip = sequence_editor.sequences.new_movie(name=f"Scene {indexScene} Shot {indexShot}", filepath=shot["video"], channel=3, frame_start=insertFrame, fit_method='FILL')
                    end_frame = int(bpy.utils.time_to_frame(shot["duration"]))
                    vid_clip.frame_final_duration = end_frame
                    insertFrame+= end_frame


        return {'FINISHED'}