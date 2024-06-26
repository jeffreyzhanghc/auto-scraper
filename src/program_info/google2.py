import http.client
import json
import asyncio
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv()
serperkey = os.getenv("serperkey")




async def serper_search(queries):
    '''
    return the first search results in serper
    '''
    payload = json.dumps([
  {
    "q": queries[0]
  },
  {
    "q": queries[1]
  },
  {
    "q": queries[2]
  },
  {
    "q": queries[3]
  }
])
    headers = {
    'X-API-KEY': f'{serperkey}',
    'Content-Type': 'application/json'
    }
    conn = http.client.HTTPSConnection("google.serper.dev")
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    search_res = res.read().decode("utf-8")
    return json.loads(search_res)

async def get_program_info(school_name,name_list):
    res = {}
    metrics= ["curriculum","degree requirements","admission requirements",""]
    metric_name = ["curriculum","DegreeReq","AdmissionReq","website"]
    program_names = name_list
    #program_names = list(set(program_names))
    for name in program_names:
        if name not in res:
            res[name] = {}
            queries = []
            for idx in range(len(metrics)):
                res[name][metric_name[idx]] = {}
                query = school_name+" "+name+""+metrics[idx]
                queries.append(query)
            search_res = await serper_search(queries)
            for idx in range(len(metrics)):
                res[name][metric_name[idx]]['link'] = None
                try:
                    res[name][metric_name[idx]]['link'] = search_res[idx]['organic'][0]['link']

                except:
                    print("capturing index error")
                    print("check answers:  ",search_res[idx])
                    print("check links:  ",res[name][metric_name[idx]]['link'])
                
    return res
    
'''
res = asyncio.run(get_program_info("Cornell University"))
with open("program_info.json", 'w') as file:
    json.dump(res,file,ensure_ascii=False, indent=4)
'''