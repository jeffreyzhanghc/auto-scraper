from trafilatura import fetch_url, extract
from playwright.async_api import async_playwright
import re
import os
import openai
from openai import OpenAI
import time
from dotenv import load_dotenv, find_dotenv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import collections
import aiohttp
import ssl
import asyncio
import certifi
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
    before_log, 
    after_log
) 
import logging
import http.client

load_dotenv()
serperkey = os.getenv("serperkey")
api_key1 = os.getenv("openaikey1")
api_key = api_key1


llogger = logging.getLogger(__name__)
@retry(wait=wait_random_exponential(min=1, max=60), 
       stop=stop_after_attempt(9), 
       retry=retry_if_exception_type(Exception))
async def call_chatgpt_async(session, names: list):
    prompt = f"""
            '''{names}'''
            Given the list of  website titles for some graduate school programs webpage, use your knowledge to accurately identify the prorgam name and 
            the degrees it offered, and return in JSON format where the name of the program is the property, and the value of the property is None.
            
            Following are some examples for four difference cases:

            Case1:, given 'Aerospace Engineering — MS'
            you should add {{"MS in Aeronautics and Astronautics (SM)": None}} as JSON elements, since you can identify easily Aerospace Engineering
            is a pair of words likely indicating program names, and MS is abbreviation of Master of Science;

            Case2:, given,'Aerospace Engineering — MS, PhD'
            you should add both {{"MS in Aeronautics and Astronautics (SM)": None}} and {{"PhD in Aeronautics and Astronautics (SM)": None}} as
            JSON elements, since can identify easily Aerospace Engineering is a pair of words likely indicating program names, and MS, PhD means it
            offer two degrees, master of science and PhD;

            Case3:, given names 'Fields of Study | Office of Graduate Education - MIT', you should NOT include because neither field of study or office of graduate education
            means a program name, it merely shows the application related information but not specific program itself.

            Case4:, given titles like 'History of Science - Princeton Graduate School', which only have program name alone without indication of degrees,you should only
            classify them as graduate programs and add something like {{"Graduate programs in Aeronautics and Astronautics": None}}, since although the program names
            is provided, there is no obvious abbreviation or direct information about the degree it offers; Normally, when you do not see abbreviation of 
            degrees such as MS, PhD, Meng, SM, MA, or other variations, you should start to consider whether the degree is given in the title names. DO NOT add non-existing degree!!!
            Carefully review the title instead of hallucinate; Another example of this case is "Transportation - MIT Office of Graduate Education", in this case you should add
            {{"Graduate programs in Transportation": None}}, because you cannot find degree related information

            Carefully follow the content of the webpage title, your goal is to REPHRASE but NOT to FABRICATE, if the information about degree offered is not clear,
            try your best to stick with original webpage title or generally classify them as 'graduate program in...'!!! Remember, giving general classification
            as graduate programs is acceptable, but generate no-clue results such as Master of Engineering in Supply Chain Management (Blended) from "Supply Chain Management Blended | Office of Graduate Education"
            is not acceptable.
            """
    payload = {
        'model': "gpt-4-0125-preview",
        'messages': [
            {"role": "user", "content": prompt}
        ],
        'response_format':{ "type": "json_object" }
    }
    try:
        async with session.post(
            url='https://api.openai.com/v1/chat/completions',
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            json=payload,
            ssl=ssl.create_default_context(cafile=certifi.where())
        ) as response:
            response = await response.json()
        if "error" in response:
            print(f"OpenAI request failed with error {response['error']}")
        return json.loads(response['choices'][0]['message']['content'])
    except:
        print("GPT program Summrization: Request failed.")


async def summarize_info(names):
    '''
    Call chatGPT for all the given prompts in parallel.
    Input: a list of parsed resume text
    Output: list of json formatted string
    '''
    async with aiohttp.ClientSession(trust_env=True) as session, asyncio.TaskGroup() as tg:
        idx = len(names)//4
        responses = {}
        #task1 = [tg.create_task(call_chatgpt_async(session, url[:idx])) for url in url_sets]
        task1 = [tg.create_task(call_chatgpt_async(session, names[:idx]))]
        task2 = [tg.create_task(call_chatgpt_async(session, names[idx:2*idx]))]
        task3 = [tg.create_task(call_chatgpt_async(session, names[2*idx:]))]
        task4 = [tg.create_task(call_chatgpt_async(session, names[3*idx:]))]
        response1 = await asyncio.gather(*task1)
        response2 = await asyncio.gather(*task2)
        response3 = await asyncio.gather(*task3)
        response4 = await asyncio.gather(*task4)
        responses.update(response1[0])
        responses.update(response2[0])
        responses.update(response3[0])
        responses.update(response4[0])
    return [responses]

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

async def get_prorgam_name(program_info,outpath):
    urls = []
    for element in program_info:
        urls.append(element[0])
    titles = {}
    names = []
    for url in urls:
        serper_res = await serper(url)
        try:
            titles[url] = serper_res['organic'][0]['title']
            names.append(serper_res['organic'][0]['title'])
        except:
            print("Serper get website name error:",serper_res)
    res = await summarize_info(names)
    '''
    json_res = []
    for i in range(len(res)):
        if res[i] != None:
            json_res.append(json.loads(res[i]))
        else:
            print("GPT fails to extract name from link:"+ urls[i])
    '''

    
    with open(outpath, 'w') as f:
            json.dump(res, f,ensure_ascii=False, indent=4)








