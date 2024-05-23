import bpy
import json
 

class GeminiChatPanel(bpy.types.Panel):
    bl_label = "Gemini Chat"
    bl_idname = "OBJECT_PT_gemini_chat"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Gemini"


    def draw(self, context):
        layout = self.layout
        scene = context.scene
        # tool = scene.myTool

        chatHistory = json.loads(context.scene.get("ChatHistory", "{}"))

        if "contents" in chatHistory:
            for content in chatHistory["contents"]:
                t = content["role"] + ": " + content["parts"][0]["text"]
                layout.label(text=t) 
        else:
            layout.label(text="\n")
    
        layout.label(text="\n")
        layout.prop(context.scene, "message_prop_ai", text="Enter Message")

        op = layout.operator("object.chatbot", text="Send Message")
        op.input_text = context.scene.message_prop_ai

    
