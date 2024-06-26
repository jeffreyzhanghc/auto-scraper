import json
import re
import subprocess
import concurrent.futures
from trafilatura import fetch_url, extract, metadata
from dotenv import load_dotenv, find_dotenv
import asyncio
import time
import logging
from asyncio import Semaphore
import datetime
import os
from .collect_seed_url import collect_seed_url
from .seed_url_detector import seed_url_detector
from .program_url_detector import detect_prorgams



def filter_url(file:str):
    '''
    Using simple regex to filter out the admission related information from outcome generated by gpt-crawler
    '''
    output = []
    pattern = re.compile(r'^(?!.*\blogin\b)(?!.*\.pdf).*(admission|undergraduate|graduate|apply|application|program)')
    
    data = json.load(open(file))
    index = list(map(lambda x: False if pattern.search(x['url']) == None else True, data))

    for i, x in enumerate(index):
        if x:
            selected_url = {}
            selected_url['title'] = data[i]['title']
            selected_url['url'] = data[i]['url']
            output.append(selected_url)

    return output


async def run_crawler_async(config,batch_size,school_name,cwd='../gpt-crawler-main'):
    '''
    Run gpt-crawler in a batched, asynchronous way
    '''
    semaphore = Semaphore(batch_size)
    async with semaphore:
        loop = asyncio.get_running_loop()
        # Prepare the environment for the subprocess
        env = os.environ.copy()  # This copies the current environment
        env['CRAWLER_CONFIG'] = json.dumps(config)  # Add your custom config
        env['school'] = school_name
        # Offload blocking operation to executor
        await loop.run_in_executor(
            None, 
            lambda: subprocess.run(["npm", "run", "start:dev"], check=True, cwd=cwd, env=env)
        )

async def simple_fetch(url):
    '''
    Simple fetch using trafilatura library to get the url
    '''
    try:

    
        downloaded = fetch_url(url)
        text = extract(downloaded,include_links= True)
        date = str(metadata.extract_metadata(downloaded).date)
        return (url,text,date)

    except Exception as e:
        return (url,None,None)  # Return None or some error indicator

async def fetch_all_urls(url_list):
    tasks = [simple_fetch(url) for url in url_list]
    # Gather all the tasks to run them concurrently
    results = await asyncio.gather(*tasks)
    return results


async def get_info(seed_url,file_name,batch_size,school_name):
    #update_config(seed_url,file_name)
    if seed_url[-1]=='/': match = seed_url+'**'
    else: match = seed_url+'/**'
    config = {
    'url': seed_url,
    'match': match,
    'maxPagesToCrawl': 200,
    'outputFileName': file_name,
    'maxTokens': 2000000
    }
    await run_crawler_async(config,batch_size,school_name)

    output = filter_url("../gpt-crawler-main/"+file_name[:-5]+"-1"+ file_name[-5:])
    url_list = list(map(lambda x: x['url'] , output))
    text_set = await fetch_all_urls(url_list)
    for i in range(len(output)):
        if text_set[i]:
            output[i]['content'] = text_set[i][1]
            output[i]['date_updated'] = text_set[i][2]
        else:
            output[i]['content'] = None
            output[i]['date_updated'] = None
    return output


async def scrawl(universities,seed_urls,gpt_selected_seed_urls,program_urls,gpt_selected_program_urls,results_path,i,end,batch_size = 3):
    a = {}
    with open(results_path, 'w') as f:
        json.dump(a, f)
    with open("../knowledge_files/side_links_records.json", 'w') as f:
        json.dump(a, f)
    start_time = time.time()
    #find the ending index
    if end!=-1 and i>=end: print("Start Index should be larger than end index")
    if end==-1 : end = len(universities)
    while i+batch_size<=end:
        batch = universities[i:i+batch_size]
        collect_seed_url(seed_urls,batch)
        await seed_url_detector(seed_urls,gpt_selected_seed_urls)
        with open(gpt_selected_seed_urls, 'r') as file:
            data = json.load(file)
        sc = []
        gu = []
        for element in data:
            sc.append(list(element.keys())[0])
            gu.append(list(element.values())[0])
        await detect_prorgams(batch,program_urls,gpt_selected_program_urls)

        with open(results_path, 'r', encoding='utf-8') as file:
            res = json.load(file)
        tasks = [get_info(url,"output"+str(j)+".json",batch_size,school) for url,school,j in zip(gu,sc,range(batch_size))]
        fetched_info = await asyncio.gather(*tasks)
        for j in range(batch_size):
            res[sc[j]] = {}
            res[sc[j]]['graduate'] = {}
            res[sc[j]]['graduate']['general_info'] = fetched_info[j]
   
        #update json
        with open(results_path, 'w', encoding='utf-8') as file:
            json.dump(res, file, ensure_ascii=False, indent=4)
        end_time = time.time()
        total_run_time = round(end_time-start_time, 3)
        print("process until school index:" +str(i+2)+'time used:'+str(total_run_time))        
        i+=batch_size


    if i < end:
        batch = universities[i:]
        collect_seed_url(seed_urls,batch)
        seed_url_detector(seed_urls,gpt_selected_seed_urls)
        with open(gpt_selected_seed_urls, 'r') as file:
            data = json.load(file)
        sc = []
        gu = []
        for element in data:
            sc.append(list(element.keys())[0])
            gu.append(list(element.values())[0])
        detect_prorgams(batch,program_urls,gpt_selected_program_urls)
        with open(results_path, 'r', encoding='utf-8') as file:
            res = json.load(file)
        tasks = [get_info(url,"output"+str(i)+".json",batch_size,school) for url,school,i in zip(gu,sc,range(end-i))]
        fetched_info = await asyncio.gather(*tasks)
        for j in range(batch_size):
            res[sc[j]] = {}
            res[sc[j]]['graduate'] = {}
            res[sc[j]]['graduate']['general_info'] = fetched_info[j]
        
        
    end_time = time.time()
    total_run_time = round(end_time-start_time, 3)
    print('task is finished in:'+str(total_run_time))
    
    


