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

        chatHistory = json.loads(scene.get("ChatHistory", "{}"))
        mainBox = layout.box()
        col = mainBox.column()
        row = col.row()

        chatBox = row.box()
        if "contents" in chatHistory:
            chatCol = chatBox.column()
            chatRow = chatCol.row()
            for content in chatHistory["contents"]:
                b = chatRow.box()
                c = b.column()
                r = c.row()
                r.label(text=content["role"])
                r = c.row()
                reply = content["parts"][0]["text"].split('\n')
                for replySentence in reply:
                    r.label(text=replySentence)
                    r = c.row()
                chatRow = chatCol.row()
            if "IsWaitingForResponse" in scene and scene["IsWaitingForResponse"] == True:
                chatRow.label(text="Waiting for Response...")
                chatRow = chatCol.row()
        else:
            chatCol = chatBox.column()
            chatRow = chatCol.row()
            chatRow.label(text="Chat History")
            layout.label(text="\n")
    
        row = col.row()
        row.prop(scene, "message_prop_ai", text="Enter Message")

        row = col.row()
        op = row.operator("object.chatbot", text="Send Message")
        op.input_text = scene.message_prop_ai
        row.operator("object.generatebasescriptfromchat", text="Generate Script")
    
