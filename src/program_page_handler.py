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

logger = logging.getLogger(__name__)
@retry(wait=wait_random_exponential(min=1, max=60), 
       stop=stop_after_attempt(9), 
       retry=retry_if_exception_type(Exception),
       before=before_log(logger, logging.DEBUG), 
       after=after_log(logger, logging.DEBUG))
async def call_chatgpt_async(session, links: list):
    '''
    This function calls gpt to select program related urls
    '''
    prompt = f"""
            '''{links}'''
            Given the list of url, select the urls that you think are related to a specific master study program. The urls should indicate
            a specific field of study. Notice that sometimes program names are in abbreviation,remember to take the abbreviation into consideration.
            Also, you may see some urls of graduate information related pages, but do not include those url since they are not related to specific major fields
            
            Return the selected in a JSON output, with PROPERTY named 'selected' and the list of selected urls as
            value. Try to make the decision fast and accurate. Provide the FULL RESULTS, DO NOT use ellipsis to skip content.
            Under standards of choosing urls contains or indicating some field-of-studies,try to include AS MANY URLS AS POSSIBLE.
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
        return json.loads(response['choices'][0]['message']['content'])['selected']
    except:
        print("Request failed.")


async def call_chatgpt_bulk(url_sets):
    '''
    Call chatGPT for all the given prompts in parallel.
    Input: a list of parsed resume text
    Output: list of json formatted string
    '''
    async with aiohttp.ClientSession(trust_env=True) as session, asyncio.TaskGroup() as tg:
        idx = len(url_sets[0])//4
        task1 = [tg.create_task(call_chatgpt_async(session, url[:idx])) for url in url_sets]
        task2 = [tg.create_task(call_chatgpt_async(session, url[idx:2*idx])) for url in url_sets]
        task3 = [tg.create_task(call_chatgpt_async(session, url[2*idx:3*idx])) for url in url_sets]
        task4 = [tg.create_task(call_chatgpt_async(session, url[3*idx:])) for url in url_sets]
        response1 = await asyncio.gather(*task1)
        response2 = await asyncio.gather(*task2)
        response3 = await asyncio.gather(*task3)
        response4 = await asyncio.gather(*task4)
        response = response1[0]+response2[0]+response3[0]+response4[0]
    return response



async def fetch_all_links(page):
    '''
    This function fecthes all the links on the input webpage
    '''
    await page.wait_for_load_state('networkidle')
    links = await page.evaluate('''() => {
        // Select all anchor tags in the body
        const anchorElements = document.body.querySelectorAll('a');
        // Map each anchor element to its href attribute
        const allLinks = Array.from(anchorElements).map(a => a.href);
        // Return the array of links
        return allLinks;
    }''')
    return links

async def fetch_with_playwright(url):
    '''
    This function use playwright to open the webpage and extract the link on the pages
    '''
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            links = await fetch_all_links(page)
            await browser.close()
            return links
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return None  # Return None or some error indicator assert the error

async def fetch_all_url(url_sets):
    '''
    Given the page urls, the funciton asynchronously extract all urls on all pages
    '''
    async with aiohttp.ClientSession(trust_env=True) as session, asyncio.TaskGroup() as tg:
        task1 = [tg.create_task(fetch_with_playwright(url[0])) for url in url_sets]
        task2 = [tg.create_task(fetch_with_playwright(url[1])) for url in url_sets]
        response1 = await asyncio.gather(*task1)
        response2 = await asyncio.gather(*task2)
    return [response1,response2]

async def get_program_branches(url_file):
    '''
    By using GPT, the function fecthes the program list url webpage and filter out the program related urls
    '''
    with open(url_file, 'r') as file:
        data = json.load(file)
    program_urls = []
    for element in data:
        url = list(element.values())[0]
        program_urls.append(url)
        print("will fetch programs from following links:",url) 
    results = []
    for program_url in program_urls:
        site1_links,site2_links = await fetch_all_url([program_url])
        if site1_links[0] == None or site2_links[0] == None:
            print("entry page cannot be fetched")
            results.append([])
        res_site1 = await call_chatgpt_bulk(site1_links)
        print(len(res_site1[0]))
        if len(res_site1[0])<40:
            print("Detect current program link numbers is smaller than 40, will include secondary entry pages")
            res_site2 = await call_chatgpt_bulk(site2_links)
            no_duplicates = list(set(res_site1+res_site2))
            results.append(no_duplicates)
        else:
            results.append(res_site1)
    return (results,program_urls)
    
'''
a,b = asyncio.run(fetch_all_url([["https://gradschool.utexas.edu/degrees-programs","https://gradschool.princeton.edu/academics/degrees-requirements/fields-study/ancient-world"]]))
res_site1 = asyncio.run(call_chatgpt_bulk(a))
print(len(res_site1))
print(res_site1)
'''










