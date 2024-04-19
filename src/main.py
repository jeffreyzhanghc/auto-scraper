
from general_info.scrawl import scrawl
from program_info.run_metrics_4prop import get_metrics4
from program_info.run_metrics_5prop import get_metrics5
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

#load variables
universities = os.getenv("universities")
seed_urls = os.getenv("seed_urls")
gpt_selected_seed_urls = os.getenv("gpt_selected_seed_urls")
program_urls = os.getenv("program_urls")
gpt_selected_program_urls = os.getenv("gpt_selected_program_urls")
final_output_path = os.getenv("final_output_path")
i = int(os.getenv('start_index'))
end = int(os.getenv('end_index'))
batch_size = int(os.getenv('batch_size'))
program_name_storage = os.getenv('program_name_storage')
file = ""
#call functions

asyncio.run(scrawl(universities,seed_urls,gpt_selected_seed_urls,program_urls,gpt_selected_program_urls,final_output_path,i,end,batch_size))
#asyncio.run(run_metrics_4prop(file))
#asyncio.run(run_metrics_5prop(file))



