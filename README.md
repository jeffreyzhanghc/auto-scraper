# Auto-Scraper <!-- omit from toc -->

Generalizale crawling methods using GPT to legally fetch admission related info for assitant use



- [Running locally](#running-locally)
  - [Clone the repository](#clone-the-repository)
  - [Install dependencies](#install-dependencies)
    - [Install dependencies for gpt-crawler](#Install-dependencies-for-gpt-crawler)
    - [Install dependencies for python scripts](#Install-dependencies-for-python-scripts)
  - [Configuration](#configuration)
  - [Run your scripts](#run-your-scripts)
- [Check your output](#check-your-output)
  

### Running locally

#### Clone the repository

Be sure you have Node.js >= 16 and Python >=3.12 installed.


```sh
git clone https://github.com/jeffreyzhanghc/auto-scraper
```

#### Install dependencies

##### Install dependencies for gpt-crawler

```sh
cd ./gpt-crawler-main
npm i
```

##### Install dependencies for python scripts

```sh
cd ./src
pip install -r requirements.txt
```


#### Configuration
Create a .env file under ./src directory, include following variables, you can copy this setting except the openaikey
```python
#openai Key
openaikey1 = "Your_OpenAI_Key"
#your seed urls file path, input for gpt to filter out the admission homepage
seed_urls = "../knowledge_files/seed_urls.json"
#path to store gpt selected homepageurl
gpt_selected_seed_urls ="../knowledge_files/gpt_selected_urls.json"
#path to store google searched program urls
program_urls = "../knowledge_files/grad_school_programs_url.json"
#path to store gpt selected program urls
gpt_selected_program_urls = "../knowledge_files/gpt_selected_programs_url.json"
#path to store final output
final_output_path = "grad_info.json"
#index in list of universities to begin crawl
i = 0
#number of universities scrawling each time, suggesting 2-5
batch_size = 2
```

#### Run your scripts
Before running, you need to acquire list of university names that you want the admissino info about and open src/main.py to modify the universities variable, an efficient way will be ask ChatGPT to get the list
```sh
cd ./src
python main.py
```

### Check your output
Under your output path, you should find output in .json with properties similar to below:
```json
{
    "University Name": {
        "graduate": {
            "general_info": [
                {
                    "title": ,
                    "url": ,
                    "content": ,
                    "date_updated": 
                },
                {
                    "title": ,
                    "url": ,
                    "content": ,
                    "date_updated": 
                }
            ],
            "program_info": []
        },
        "Date_fetched": 
    }
}

```