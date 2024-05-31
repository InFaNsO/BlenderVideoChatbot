import bpy
import requests
import json
from .LocalVariables import google_api_key as key

chatHistoryStr = "ChatHistory"
chatData = {
   "contents": [
      
   ]
}


class GeminiChatOperator(bpy.types.Operator):
   bl_idname = "object.chatbot"
   bl_label = "ChatBot"

   input_text: bpy.props.StringProperty(name="Text Input") # type: ignore
   firstTime = True

   def execute(self, context):
      global chatData 
      tex = self.input_text
      context.scene.message_prop_ai = ""
      
      print("InputText Set by panel: ", self.input_text)

      if self.firstTime == True and context.scene.get("ChatHistory"):
         chatData=json.loads(context.scene.get("ChatHistory", "{}"))
         self.firstTime = False

      chatData["contents"].append(GetData(tex, "user"))     
      print("Sending following Request to google\n")

      print(json.dumps(chatData))

      response = requests.post(url, headers=header, data=json.dumps(chatData))
      if response.status_code == 200:
         print("Request Sucessfull!!")
         print("Response Body: \n",response.json())
         chatData["contents"].append(GetData(response.json()["candidates"][0]["content"]["parts"][0]["text"], "model"))
         print(chatData)
      else:
         print("Request failed with status code:", response.status_code)
         print("Response body:", response.text)

      d_json = json.dumps(chatData)
      context.scene["ChatHistory"] = d_json
      print(json.loads(context.scene.get("ChatHistory"), indent=4))
      context.scene["IsWaitingForResponse"] = False

      return {'FINISHED'}
   

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}"

header = {
    "Content-Type": "application/json"
}

d = {
   "contents": [
      
   ],
   "safetySettings": [
      {
         "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
         "threshold": "BLOCK_NONE"
      },
      {
         "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
         "threshold": "BLOCK_NONE"
      },
      {
         "category": "HARM_CATEGORY_HATE_SPEECH",
         "threshold": "BLOCK_NONE"
      },
      {
         "category": "HARM_CATEGORY_HARASSMENT",
         "threshold": "BLOCK_NONE"
      }
      ]
}

def GetData(text, role):
    data = {
       "role": role,
       "parts": [
          { "text": text}
       ]
    }
    return data


