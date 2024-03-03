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
  },
  {
    "q": queries[4]
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
    metrics= ["Deadline","TOEFL/IELTS test score requirement","GRE test score requirement","prerequisite course","letters of recommendations"]
    metric_name = ["Deadline","TOEFLRequirement","GRERequirement","prerequisiteCourse","recommendations"]
    with open(name_list, 'r') as file:
        data = json.load(file)
    program_names = []
    for dat in data:
        program_names.append(list(dat.keys())[0])
    program_names = list(set(program_names))
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
                res[name][metric_name[idx]]['link'] = search_res[idx]['organic'][0]['link']
                
    return res
    
'''
res = asyncio.run(get_program_info("Cornell University"))
with open("program_info.json", 'w') as file:
    json.dump(res,file,ensure_ascii=False, indent=4)
'''