import os
import json
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search, FunctionTool
from google.genai import types
from .tools.mcp_client_tool import trends_tool

# --- 1. Import your utility ---
try:
    from utils import load_instruction_from_file
except ImportError:
    from .utils import load_instruction_from_file

load_dotenv()

# --- 2. Helper to make paths cleaner ---
def get_prompt(filename):
    path_to_file = os.path.join("prompts", filename)
    return load_instruction_from_file(path_to_file)

# --- 3. Configuration ---
retry_config = types.HttpRetryOptions(
    attempts=3, exp_base=2, initial_delay=1, http_status_codes=[429, 500, 503]
)

model_reasoning = Gemini(model="gemini-2.0-flash", retry_options=retry_config) 
model_fast = Gemini(model="gemini-2.0-flash-lite", retry_options=retry_config)

# --- 4. Critical Logic Tools ---

def init_state_vars():
    """Seeds the session state with a dummy critique to prevent crashes."""
    return json.dumps({
        "total_score": 0, 
        "feedback": "Initial draft - pending review."
    })

def exit_loop():
    """The Refiner calls this tool when the script score is high enough (>= 8)."""
    return "Loop Exited: Quality Standard Met."

# --- AGENTS ---

# 0. Memory Coordinator (checks for cached research)
memory_coordinator = Agent(
    name="MemoryCoordinator",
    model=model_fast,  # No tools needed, just session context
    instruction=get_prompt("memory_coordinator.txt"),
    output_key="memory_check"
)

# 1. Researcher
researcher = Agent(
    name="Researcher",
    model=model_reasoning,
    instruction=get_prompt("researcher.txt"),
    tools=[trends_tool],  # Can't mix multiple tool types in gemini-2.0-flash
    output_key="content_brief"
)

# 2. ScriptWriter
scriptwriter = Agent(
    name="ScriptWriter",
    model=model_reasoning,
    instruction=get_prompt("scriptwriter.txt"),
    output_key="current_script"
)

# 3. Bootstrapper
bootstrapper = Agent(
    name="StateInitializer",
    model=model_reasoning,  # MUST use reasoning model for tool support
    instruction="Call the init_state_vars tool immediately. Do not output text.",
    tools=[FunctionTool(init_state_vars)],
    output_key="critique_result" 
)

# 4. The Supervisor (Critic)
critic = Agent(
    name="ViralityJudge",
    model=model_reasoning, 
    instruction=get_prompt("judge.txt"),
    output_key="critique_result" 
)

# 5. The Refiner
refiner = Agent(
    name="ScriptRefiner",
    model=model_reasoning,  # MUST use reasoning model for exit_loop tool
    instruction=get_prompt("refiner.txt"),
    output_key="current_script",
    tools=[FunctionTool(exit_loop)]
)

# 6. Visualizer
visualizer = Agent(
    name="Visualizer",
    model=model_fast,
    instruction=get_prompt("visualizer.txt"),
    output_key="visual_plan"
)

# 7. Formatter
formatter = Agent(
    name="Formatter",
    model=model_fast,
    instruction=get_prompt("formatter.txt"),
    output_key="final_output"
)

# --- ARCHITECTURE FLOW ---

quality_loop = LoopAgent(
    name="QualityControlLoop",
    sub_agents=[critic, refiner],
    max_iterations=3
)

root_agent = SequentialAgent(
    name="Youtube_Agent",
    sub_agents=[
        memory_coordinator,  # Check for cached research first
        researcher,
        scriptwriter,
        bootstrapper,
        quality_loop,
        visualizer,
        formatter
    ]
)