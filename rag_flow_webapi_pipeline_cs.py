"""
title: RagFlow Pipeline
author: open-webui
date: 2025-10-30
version: 1.1
license: MIT
description: A pipeline for retrieving relevant information from a knowledge base using the RagFlow's Agent Interface.
requirements: ragflow_sdk, datasets>=2.6.1, sentence-transformers>=2.2.0
"""
#智能客服
from typing import List, Union, Generator, Iterator, Optional
from pydantic import BaseModel
import requests
import json
#API_KEY: ragflow apikey
#AGENT_ID: ragflow agentid
#HOST: ragflow host
#PORT: ragflow port
class Pipeline:
    class Valves(BaseModel):
        API_KEY: str
        AGENT_ID: str
        HOST: str
        PORT: str

    def __init__(self):
        self.session_id=None
        self.debug=True
        self.sessionKV={}
        self.valves = self.Valves(
            **{
                "API_KEY": "",
                "AGENT_ID": "",
                "HOST":"",
                "PORT":""
            }
        )

    async def on_startup(self):
        pass

    async def on_shutdown(self):
        # This function is called when the server is stopped.
        pass
    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        # This function is called before the OpenAI API request is made. You can modify the form data before it is sent to the OpenAI API.
        print(f"inlet: {__name__}")
        if self.debug:
            chat_id=body['metadata']['chat_id']
            print(f"inlet: {__name__} - chat_id:{chat_id}")
            if self.sessionKV.get(chat_id):
                self.session_id=self.sessionKV.get(chat_id)
                print(f"cache ragflow's session_id is : {self.session_id}")
            else:
                #创建session
                session_url = f"{self.valves.HOST}:{self.valves.PORT}/api/v1/agents/{self.valves.AGENT_ID}/sessions"
                session_headers = {
                    'content-Type': 'application/json',
                    'Authorization': 'Bearer '+self.valves.API_KEY
                }
                session_data={}
                session_response = requests.post(session_url, headers=session_headers, json=session_data)
                json_res=json.loads(session_response.text)
                self.session_id=json_res['data']['id']
                self.sessionKV[chat_id]=self.session_id
                print(f"new ragflow's session_id is : {json_res['data']['id']}")
            #print(f"inlet: {__name__} - body:{body}")
            print(f"inlet: {__name__} - user:")
            print(user)
        return body

    async def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        # This function is called after the OpenAI API response is completed. You can modify the messages after they are received from the OpenAI API.
        print(f"outlet: {__name__}")
        if self.debug:
            print(f"outlet: {__name__} - body:")
            #print(body)
            print(f"outlet chat_id: {body['chat_id']}")
            print(f"outlet session_id: {body['session_id']}")
            print(f"outlet: {__name__} - user:")
            print(user)
        return body
    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        # This is where you can add your custom RAG pipeline.
        # Typically, you would retrieve relevant information from your knowledge base and synthesize it to generate a response.
        # print(messages)
        question_url = f"{self.valves.HOST}:{self.valves.PORT}/api/v1/agents/{self.valves.AGENT_ID}/completions"
        question_headers = {
            'content-Type': 'application/json',
            'Authorization': 'Bearer '+self.valves.API_KEY
        }
        question_data={'question':user_message,
                       'stream':True,
                       'session_id':self.session_id,
                       'lang':'Chinese'}
        question_response = requests.post(question_url, headers=question_headers,stream=True, json=question_data)
        if question_response.status_code == 200:
            # Process and yield each chunk from the response
            for line in question_response.iter_lines():
                if line :
                    try:
                        # Remove 'data: ' prefix and parse JSON
                        #print("line is :",line.decode('utf-8'))

                        json_data_str=line.decode('utf-8')[5:]
                        if json_data_str=='' or json_data_str=='[DONE]':
                            continue
                        json_data = json.loads(json_data_str)
                        #print("json_data is :",json_data)
                        # Extract and yield only the 'text' field from the nested 'data' object
                        # print reference
                        if 'data' in json_data and json_data['data'] is not True and 'content' in json_data['data'] and '* is running...' not in json_data['data']['content'] :
                            yield json_data['data']['content']
                        elif json_data.get('data', {}).get('reference'):
                                referenceStr="\n\n### references\n\n"
                                filesList=[]
                                for chunk in json_data['data']['reference']['chunks']:
                                    print(f"chunks is :{json_data['data']['reference']['chunks']}")
                                    if chunk['document_id'] not in filesList:
                                        filename = chunk['document_name']
                                        parts = filename.split('.')
                                        last_part = parts[-1].strip()
                                        ext= last_part.lower() if last_part else ''
                                        referenceStr=referenceStr+f"\n\n - ["+chunk['document_name']+f"]({self.valves.HOST}:{self.valves.PORT}/document/{chunk['document_id']}?ext={ext}&prefix=document)"
                                        filesList.append(chunk['document_id'])
                                #print(f"chunks is :{len(json_data['data']['reference']['chunks'])}")
                                yield referenceStr
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON: {line}")
        else:
            yield f"Workflow request failed with status code: {question_response.status_code}"
