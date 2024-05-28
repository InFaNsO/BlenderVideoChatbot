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
        mainBox = layout.box()
        col = mainBox.column()
        row = mainBox.row()

        chatBox = row.box()
        if "contents" in chatHistory:
            chatCol = chatBox.column()
            chatRow = chatCol.row()
            for content in chatHistory["contents"]:
                t = content["role"] + ": " + content["parts"][0]["text"]
                chatRow.label(text=t)
                chatRow = chatCol.row() 
        else:
            chatCol = chatBox.column()
            chatRow = chatCol.row()
            chatRow.label(text="Chat History")
            layout.label(text="\n")
    
        row = col.row()
        row.prop(context.scene, "message_prop_ai", text="Enter Message")

        row = col.row()
        op = row.operator("object.chatbot", text="Send Message")
        op.input_text = context.scene.message_prop_ai
        op = row.operator("object.generatebasescript", text="Generate Script")
    
