import asyncio
import os
from dataclasses import asdict
from typing import List, Union, Optional
from dotenv import load_dotenv
import random
import async_timeout
from openai import OpenAI, AsyncOpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
import time
from typing import Dict, Any

from swarm.utils.log import logger
from swarm.llm.format import Message
from swarm.llm.price import cost_count
from swarm.llm.llm import LLM
from swarm.llm.llm_registry import LLMRegistry


LM_STUDIO_URL = "http://localhost:1234/v1"
OLLAMA_URL = "http://localhost:11434/v1"

load_dotenv(override=True)
OPENAI_API_KEYS=[os.getenv(f"OPENAI_API_KEY")]
for i in range(10):
    if os.getenv(f"OPENAI_API_KEY{i}"):
        OPENAI_API_KEYS.append(os.getenv(f"OPENAI_API_KEY{i}"))


def gpt_chat(
    model: str,
    messages: List[Message],
    max_tokens: int = 8192,
    temperature: float = 0.0,
    num_comps=1,
    return_cost=False,
) -> Union[List[str], str]:
    if messages[0].content == '$skip$':
        return ''

    api_kwargs: Dict[str, Any]
    if model == "lmstudio":
        api_kwargs = dict(base_url=LM_STUDIO_URL)
    elif model == "ollama":
        api_kwargs = dict(base_url=OLLAMA_URL)
    else:
        api_key = random.sample(OPENAI_API_KEYS, 1)[0]
        api_kwargs = dict(api_key=api_key)
    client = OpenAI(**api_kwargs)

    formated_messages = [asdict(message) for message in messages]
    start_time = time.time()
    response = client.chat.completions.create(model=model,
    messages=formated_messages,
    max_tokens=max_tokens,
    temperature=temperature,
    top_p=1,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    n=num_comps)
    end_time = time.time()
    if num_comps == 1:
        cost_count(response, model, start_time, end_time)
        return response.choices[0].message.content

    cost_count(response, model, start_time, end_time)

    return [choice.message.content for choice in response.choices]


@retry(wait=wait_random_exponential(max=100), stop=stop_after_attempt(10))
async def gpt_achat(
    model: str,
    messages: List[Message],
    max_tokens: int = 8192,
    temperature: float = 0.0,
    num_comps=1,
    return_cost=False,
) -> Union[List[str], str]:
    if messages[0].content == '$skip$':
        return '' 

    api_kwargs: Dict[str, Any]
    if model == "lmstudio":
        api_kwargs = dict(base_url=LM_STUDIO_URL)
    elif model.startswith("gpt"):
        api_key = random.sample(OPENAI_API_KEYS, 1)[0]
        api_kwargs = dict(api_key=api_key)
    else:
        api_kwargs = dict(base_url=OLLAMA_URL)
    aclient = AsyncOpenAI(**api_kwargs)

    formated_messages = [asdict(message) for message in messages]
    start_time = time.time()
    try:
        async with async_timeout.timeout(1000):
            response = await aclient.chat.completions.create(model=model,
            messages=formated_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            n=num_comps)
    except asyncio.TimeoutError:
        print('Timeout')
        raise TimeoutError("GPT Timeout")
    end_time = time.time()
    if num_comps == 1:
        cost_count(response, model, start_time, end_time)
        return response.choices[0].message.content
    cost_count(response, model, start_time, end_time)

    return [choice.message.content for choice in response.choices]


@LLMRegistry.register('GPTChat')
class GPTChat(LLM):

    def __init__(self, model_name: str):
        self.model_name = model_name

    async def agen(
        self,
        messages: List[Message],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        num_comps: Optional[int] = None,
        ) -> Union[List[str], str]:

        if max_tokens is None:
            max_tokens = self.DEFAULT_MAX_TOKENS
        if temperature is None:
            temperature = self.DEFAULT_TEMPERATURE
        if num_comps is None:
            num_comps = self.DEFUALT_NUM_COMPLETIONS

        if isinstance(messages, str):
            messages = [Message(role="user", content=messages)]

        return await gpt_achat(self.model_name,
                               messages,
                               max_tokens,
                               temperature,
                               num_comps)

    def gen(
        self,
        messages: List[Message],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        num_comps: Optional[int] = None,
        ) -> Union[List[str], str]:

        if max_tokens is None:
            max_tokens = self.DEFAULT_MAX_TOKENS
        if temperature is None:
            temperature = self.DEFAULT_TEMPERATURE
        if num_comps is None:
            num_comps = self.DEFUALT_NUM_COMPLETIONS

        if isinstance(messages, str):
            messages = [Message(role="user", content=messages)]

        return gpt_chat(self.model_name,
                        messages, 
                        max_tokens,
                        temperature,
                        num_comps)
