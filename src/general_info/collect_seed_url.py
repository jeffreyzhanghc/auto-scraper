from googlesearch import search
import asyncio
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
    before_log, 
    after_log
) 
import json


def collect_seed_url(path,universities):
    a = {}
    with open(path, 'w') as f:
        json.dump(a, f)
    with open(path, 'r') as file:
        dict = json.load(file)
    dict = {}
    for university in universities:
        query = f"{university} Graduate Admission Homepage"
        dict[university] =[]
        for j in search(query,num_results = 1):
            print("Collecting HomePage URL for" + str(university)+": "+str(j))
            dict[university].append(j)
    with open(path, 'w', encoding='utf-8') as f:
            json.dump(dict, f, ensure_ascii=False, indent=4)


