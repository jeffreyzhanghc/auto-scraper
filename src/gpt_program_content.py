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


load_dotenv()
api_key1 = os.getenv("openaikey1")
api_key = api_key1


llogger = logging.getLogger(__name__)
@retry(wait=wait_random_exponential(min=1, max=60), 
       stop=stop_after_attempt(9), 
       retry=retry_if_exception_type(Exception))
async def call_chatgpt_async(session, url: str):
    prompt = f"""
            '''{url}'''
            Given the entry link of a school program, use your knowledge to accurately identify the prorgam name and the degreee offered, and return
            in JSON format where the name of the program is the property, and the value of the property is None.
            for example:
            "https://gradschool.cornell.edu/academics/fields-of-study/subject/africana-studies/africana-studies-phd-ithaca"
            you should return: {{"Africana Studies Ph.D": None}}


            """
    payload = {
        'model': "gpt-4-1106-preview",
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
        return response['choices'][0]['message']['content']
    except:
        print("GPT program Summrization: Request failed.")


async def summarize_info(info_sets):
    '''
    Call chatGPT for all the given prompts in parallel.
    Input: a list of parsed resume text
    Output: list of json formatted string
    '''
    async with aiohttp.ClientSession(trust_env=True) as session, asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(call_chatgpt_async(session, info)) for info in info_sets]
        responses = await asyncio.gather(*tasks)
    return responses



async def get_prorgam_name(program_info,outpath):
    urls = []
    for element in program_info:
        urls.append(element[0])
    res = await summarize_info(urls)
    json_res = []
    for i in range(len(res)):
        if res[i] != None:
            json_res.append(json.loads(res[i]))
        else:
            print("GPT fails to extract name from link:"+ urls[i])
    with open(outpath, 'w') as f:
            json.dump(json_res, f,ensure_ascii=False, indent=4)






