import bpy

apiKey = "uWby7NPaTxbZyq4jZZ7w28PjkNJnkheZlaGamaUfelvVEUiIRVKKipeF"


class PexelsVideoOperatorOperator(bpy.types.Operator):
    bl_idname = "object.pexelsvideooperator"
    bl_label = "PexelsVideoOperator"

    test = ""

    def execute(self, context):
        return {'FINISHED'}
