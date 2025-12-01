import os
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv() 

from google.adk.agents import Agent, SequentialAgent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search, FunctionTool
from google.genai import types

# 2. Import your file reader
# Ensure utils.py is in the same folder as agent.py
try:
    from utils import load_instruction_from_file
except ImportError:
    from .utils import load_instruction_from_file

# --- Helper to make paths cleaner ---
def get_prompt(filename):
    """Reads a file from the 'prompts/' directory."""
    return load_instruction_from_file(os.path.join("prompts", filename))

# --- Configuration ---
retry_config = types.HttpRetryOptions(
    attempts=3, exp_base=2, initial_delay=1, http_status_codes=[429, 500, 503]
)

model_default = Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)
model_smart = model_default  # Use Flash-lite for the Judge temporarily
model_fast = model_default
# model_fast = Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)
# model_smart = Gemini(model="gemini-2.5-pro-preview-03-25", retry_options=retry_config)

# --- Tools ---
def exit_loop():
    return {"status": "approved", "message": "Exiting loop."}

# --- Agents (Now loading from files) ---

scriptwriter = Agent(
    name="ScriptWriter",
    model=model_fast,
    instruction=get_prompt("scriptwriter.txt"),
    tools=[google_search], 
    output_key="current_script"
)

critic = Agent(
    name="ViralityJudge",
    model=model_smart,
    instruction=get_prompt("judge.txt"),
    output_key="critique"
)

refiner = Agent(
    name="ScriptRefiner",
    model=model_fast,
    instruction=get_prompt("refiner.txt"),
    output_key="current_script",
    tools=[FunctionTool(exit_loop)]
)

visualizer = Agent(
    name="Visualizer",
    model=model_fast,
    instruction=get_prompt("visualizer.txt"),
    output_key="visual_plan"
)

formatter = Agent(
    name="Formatter",
    model=model_fast,
    instruction=get_prompt("formatter.txt"),
    output_key="final_output"
)

# --- Architecture ---

refinement_loop = LoopAgent(
    name="QualityLoop",
    sub_agents=[critic, refiner],
    max_iterations=3
)

root_agent = SequentialAgent(
    name="YouTubeShortsTeam",
    sub_agents=[
        scriptwriter,
        refinement_loop,
        visualizer,
        formatter
    ]
)