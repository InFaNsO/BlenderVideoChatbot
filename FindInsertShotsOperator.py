import bpy
import json
import requests


class FindInsertShotsOperator(bpy.types.Operator):
    bl_idname = "object.findinsertshots"
    bl_label = "FindInsertShots"

    def execute(self, context):
        return {'FINISHED'}
