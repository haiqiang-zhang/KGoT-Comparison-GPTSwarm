#!/usr/bin/env python
# -*- coding: utf-8 -*-

from swarm.utils.log import swarmlog
from swarm.utils.globals import Cost, PromptTokens, CompletionTokens, UsageStatisticsObject
import inspect
# GPT-4:  https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo
# GPT-4o-mini: https://platform.openai.com/docs/models/gpt-4o-mini
# GPT3.5: https://platform.openai.com/docs/models/gpt-3-5
# DALL-E: https://openai.com/pricing




def cost_count(response, model_name, start_time, end_time):
    print("cost_count")
    print(type(response))
    print(response)
    branch: str
    prompt_len: int
    completion_len: int
    price: float
    
    # get the caller function name
    callers_function_name_list = []
    for frame_info in inspect.stack()[1:6]:
        frame = frame_info.frame
        func_name = frame_info.function
        cls_name = None
        
        # Check if 'self' is in local variables -> instance method
        if 'self' in frame.f_locals:
            cls_name = frame.f_locals['self'].__class__.__name__
        # Check if 'cls' is in locals -> class method
        elif 'cls' in frame.f_locals:
            cls_name = frame.f_locals['cls'].__name__

        if cls_name:
            names = f"{cls_name}.{func_name}"
        else:
            names = func_name
            
        if "AsyncRetrying" in names or "GPTChat" in names:
            continue
        
        callers_function_name_list.append(names)

    caller_function_name = "->".join(callers_function_name_list)
    
    if "gpt-4o" in model_name:
        try:
            branch = "gpt-4o"
            prompt_len = response.usage.prompt_tokens
            completion_len = response.usage.completion_tokens
            price = prompt_len * OPENAI_MODEL_INFO[branch][model_name]["input"] /1000 + \
            completion_len * OPENAI_MODEL_INFO[branch][model_name]["output"] /1000
        except:
            branch = "gpt-4o"
            prompt_len = response["usage"]["prompt_tokens"]
            completion_len = response["usage"]["completion_tokens"]
            price = prompt_len * OPENAI_MODEL_INFO[branch][model_name]["input"] /1000 + \
                completion_len * OPENAI_MODEL_INFO[branch][model_name]["output"] /1000
    elif "gpt-4" in model_name:
        try:
            branch = "gpt-4"
            prompt_len = response.usage.prompt_tokens
            completion_len = response.usage.completion_tokens
            price = prompt_len * OPENAI_MODEL_INFO[branch][model_name]["input"] /1000 + \
                completion_len * OPENAI_MODEL_INFO[branch][model_name]["output"] /1000
        except:
            branch = "gpt-4"
            prompt_len = response["usage"]["prompt_tokens"]
            completion_len = response["usage"]["completion_tokens"]
            price = prompt_len * OPENAI_MODEL_INFO[branch][model_name]["input"] /1000 + \
                completion_len * OPENAI_MODEL_INFO[branch][model_name]["output"] /1000
    elif "gpt-3.5" in model_name:
        branch = "gpt-3.5"
        prompt_len = response.usage.prompt_tokens
        completion_len = response.usage.completion_tokens
        price = prompt_len * OPENAI_MODEL_INFO[branch][model_name]["input"] /1000 + \
            completion_len * OPENAI_MODEL_INFO[branch][model_name]["output"] /1000
    elif "dall-e" in model_name:
        branch = "dall-e"
        price = 0.0
        prompt_len = 0
        completion_len = 0
    else:
        try:
            branch = "other"
            price = 0.0
            prompt_len = response.usage.prompt_tokens
            completion_len = response.usage.completion_tokens
        except:
            branch = "other"
            price = 0.0
            prompt_len = response["usage"]["prompt_tokens"]
            completion_len = response["usage"]["completion_tokens"]
        
    usage_statistics = UsageStatisticsObject.instance().value
    usage_statistics.log_statistic(
                    function_name=caller_function_name,
                    start_time=start_time,
                    end_time=end_time,
                    model=model_name,
                    prompt_tokens=prompt_len,
                    completion_tokens=completion_len,
                    cost=price,
                )

    Cost.instance().value += price
    PromptTokens.instance().value += prompt_len
    CompletionTokens.instance().value += completion_len

    # print(f"Prompt Tokens: {prompt_len}, Completion Tokens: {completion_len}")
    return price, prompt_len, completion_len

OPENAI_MODEL_INFO ={
    "gpt-4": {
        "current_recommended": "gpt-4-1106-preview",
        "gpt-4-0125-preview": {
            "context window": 128000, 
            "training": "Jan 2024", 
            "input": 0.01, 
            "output": 0.03
        },      
        "gpt-4-1106-preview": {
            "context window": 128000, 
            "training": "Apr 2023", 
            "input": 0.01, 
            "output": 0.03
        },
        "gpt-4-vision-preview": {
            "context window": 128000, 
            "training": "Apr 2023", 
            "input": 0.01, 
            "output": 0.03
        },
        "gpt-4": {
            "context window": 8192, 
            "training": "Sep 2021", 
            "input": 0.03, 
            "output": 0.06
        },
        "gpt-4-0314": {
            "context window": 8192, 
            "training": "Sep 2021", 
            "input": 0.03, 
            "output": 0.06
        },
        "gpt-4-32k": {
            "context window": 32768, 
            "training": "Sep 2021", 
            "input": 0.06, 
            "output": 0.12
        },
        "gpt-4-32k-0314": {
            "context window": 32768, 
            "training": "Sep 2021", 
            "input": 0.06, 
            "output": 0.12
        },
        "gpt-4-0613": {
            "context window": 8192, 
            "training": "Sep 2021", 
            "input": 0.06, 
            "output": 0.12
        }
    },
    "gpt-4o": { 
        "gpt-4o-mini": {
            "context window": 128000,
            "input": 0.00015,
            "output": 0.0006
        }
    },
    "gpt-3.5": {
        "current_recommended": "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-0125": {
            "context window": 16385, 
            "training": "Jan 2024", 
            "input": 0.0010, 
            "output": 0.0020
        },
        "gpt-3.5-turbo-1106": {
            "context window": 16385, 
            "training": "Sep 2021", 
            "input": 0.0010, 
            "output": 0.0020
        },
        "gpt-3.5-turbo-instruct": {
            "context window": 4096, 
            "training": "Sep 2021", 
            "input": 0.0015, 
            "output": 0.0020
        },
        "gpt-3.5-turbo": {
            "context window": 4096, 
            "training": "Sep 2021", 
            "input": 0.0015, 
            "output": 0.0020
        },
        "gpt-3.5-turbo-0301": {
            "context window": 4096, 
            "training": "Sep 2021", 
            "input": 0.0015, 
            "output": 0.0020
        },
        "gpt-3.5-turbo-0613": {
            "context window": 16384, 
            "training": "Sep 2021", 
            "input": 0.0015, 
            "output": 0.0020
        },
        "gpt-3.5-turbo-16k-0613": {
            "context window": 16384, 
            "training": "Sep 2021", 
            "input": 0.0015, 
            "output": 0.0020
        }
    },
    "dall-e": {
        "current_recommended": "dall-e-3",
        "dall-e-3": {
            "release": "Nov 2023",
            "standard": {
                "1024×1024": 0.040,
                "1024×1792": 0.080,
                "1792×1024": 0.080
            },
            "hd": {
                "1024×1024": 0.080,
                "1024×1792": 0.120,
                "1792×1024": 0.120
            }
        },
        "dall-e-2": {
            "release": "Nov 2022",
            "1024×1024": 0.020,
            "512×512": 0.018,
            "256×256": 0.016
        }
    }
}



