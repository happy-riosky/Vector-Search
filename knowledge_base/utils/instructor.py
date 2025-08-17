import os
import instructor
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
open_model = "gpt-4o-mini"

deepseek_client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("DEEPSEEK_BASE_URL"))
deepseek_model = "deepseek-chat"

default_client = openai_client
default_model = open_model


instructor_client = instructor.from_openai(OpenAI(api_key=os.getenv("OPENAI_API_KEY")))
