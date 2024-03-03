import os
import subprocess
from openai import OpenAI
import json
from portkey_ai import createHeaders, PORTKEY_GATEWAY_URL

import constants
os.environ["OPENAI_API_KEY"] = constants.OPENAI_KEY
os.environ["PORTKEY_API_KEY"] = constants.PORTKEY_KEY

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=PORTKEY_GATEWAY_URL,
    default_headers=createHeaders(
        provider="openai",
        api_key=os.environ.get("PORTKEY_API_KEY")
    )
)

def execute_shell_command(cmd:str) -> str:
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()  # Return the output of the command
        else:
            return f"Error executing command: {command}"
    except Exception as e:
        return f"An error occurred: {e}"

def get_sys_info() -> str:
    print("get_sys_info")
    info = {
        "uname_output": "Linux agrippa 6.5.0-21-generic #21~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC Fri Feb  9 13:32:52 UTC 2 x86_64 x86_64 x86_64 GNU/Linux",
        "os": "Linux",
        "arch": "x86_64",
        "cores": "8",
        "df_output": """
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           3,2G  2,4M  3,2G   1% /run
/dev/nvme0n1p5  457G  152G  283G  35% /
tmpfs            16G  191M   16G   2% /dev/shm
tmpfs           5,0M  4,0K  5,0M   1% /run/lock
efivarfs        256K   46K  206K  19% /sys/firmware/efi/efivars
/dev/nvme0n1p1   96M   32M   65M  33% /boot/efi
tmpfs           3,2G  164K  3,2G   1% /run/user/1000
""",
        "lshw_output": """
  *-display                 
       description: VGA compatible controller
       product: GP106 [GeForce GTX 1060 6GB] [10DE:1C03]
       vendor: NVIDIA Corporation [10DE]
       physical id: 0
       bus info: pci@0000:02:00.0
       version: a1
       width: 64 bits
       clock: 33MHz
       capabilities: pm msi pciexpress vga_controller bus_master cap_list rom
       configuration: driver=nvidia latency=0
       resources: irq:146 memory:dd000000-ddffffff memory:c0000000-cfffffff memory:d0000000-d1ffffff ioport:e000(size=128) memory:c0000-dffff
  *-graphics
       product: EFI VGA
       physical id: 2
       logical name: /dev/fb0
       capabilities: fb
       configuration: depth=32 resolution=1024,768
"""
        }
    return json.dumps(info)

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    print("get_current_weather")
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

def run_conversation():

    # Step 1: send the conversation and available functions to the model
    messages = [
      {
        "role": "system",
        "content": "You are a pessimistic assistant. You keep factual answers short but add remarks with sentiment."
      },
      #{"role": "user", "content": "What's the weather like in San Francisco, and Paris?"}
      #{"role": "user", "content": "Should I upgrade to a newer operating system?"}
      #{"role": "user", "content": "What is the name of my Linux distribution and version nickname?"}
      #{"role": "user", "content": "3 CPU bound processes are already running and I want to start 7 more. Can all those processes run concurrently?"}
      {"role": "user", "content": "Could I run a big LLM locally on my computer?"}
      ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_sys_info",
                "description": "Get information about my computer"
            },
        }
    ]
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
        #tool_choice={"type": "function", "function": {"name": "get_sys_info"}}
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
            "get_sys_info": get_sys_info
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            if function_to_call == get_current_weather:
                function_response = function_to_call(
                    location=function_args.get("location"),
                    unit=function_args.get("unit"),
                )
            else:
                function_response = function_to_call()
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response
    else:
        return response_message
print(run_conversation())