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
            Given the list of url, select the urls that you think are related to a specific graduate study program. The urls should indicate
            a specific field of study, return the selected in a JSON output, with PROPERTY named 'selected' and the list of selected urls as
            value. Try to make the decision fast and efficiently with accuracy. 
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
        return json.loads(response['choices'][0]['message']['content'])['selected']
    except:
        print("Request failed.")


async def call_chatgpt_bulk(url_sets):
    '''
    Call chatGPT for all the given prompts in parallel.
    Input: a list of parsed resume text
    Output: list of json formatted string
    '''
    async with aiohttp.ClientSession() as session, asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(call_chatgpt_async(session, url)) for url in url_sets]
        responses = await asyncio.gather(*tasks)
    return responses



async def fetch_all_links(page):
    '''
    This function fecthes all the links on the input webpage
    '''
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
    async with aiohttp.ClientSession() as session, asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_with_playwright(url)) for url in url_sets]
        responses = await asyncio.gather(*tasks)
    return responses

async def get_program_branches(url_file,start_index, batch_size):
    '''
    By using GPT, the function fecthes the program list url webpage and filter out the program related urls
    '''
    with open(url_file, 'r') as file:
        data = json.load(file)
    schools = list(data.keys())
    program_urls = []
    for school in schools:
        program_urls.append(data[school][0])   
    all_links = await fetch_all_url(program_urls[start_index:start_index+batch_size])
    results = await call_chatgpt_bulk(all_links)
    return results
    
    