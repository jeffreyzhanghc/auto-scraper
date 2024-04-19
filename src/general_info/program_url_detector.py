import sys
#must be python 3.11 or above to use some of the library
print(sys.version)

import re
import os
import openai
from openai import OpenAI
import time
from dotenv import load_dotenv, find_dotenv
import json
import http.client
import json
import asyncio
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv()
serperkey = os.getenv("serperkey")


async def serper(queries):
    '''
    return the first search results in serper
    '''
    payload = json.dumps(
  {
    "q": queries
  })
    headers = {
    'X-API-KEY': f'{serperkey}',
    'Content-Type': 'application/json'
    }
    conn = http.client.HTTPSConnection("google.serper.dev")
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    search_res = res.read().decode("utf-8")
    return json.loads(search_res)

async def google_program_url(path,universities):
    with open("../knowledge_files/side_links_records.json", 'r') as file:
      side_links = json.load(file)
    dict = []
    for university in universities:
        query = f"{university} master majors list"
        serper_res = await serper(query)
        organic1 = serper_res['organic'][0]['link']
        organic2 = serper_res['organic'][1]['link']
        if 'sitelinks' in serper_res['organic'][0]:
            side_links[university] = serper_res['organic'][0]['sitelinks']
        value = {university:[organic1,organic2]}
        dict.append(value)
    with open("../knowledge_files/side_links_records.json", 'w') as file:
       json.dump(side_links, file, indent=4)
    with open(path, 'w', encoding='utf-8') as f:
       json.dump(dict, f, ensure_ascii=False, indent=4)

async def detect_prorgams(universities,inpath,outpath):
    await google_program_url(outpath,universities)


    







