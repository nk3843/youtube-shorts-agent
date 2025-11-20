from google.adk.agents import Agent, SequentialAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from .utils import load_instruction_from_file


#---Scriptwriter Sub Agent----
scriptwriter_agent = Agent(
    name="ShortScriptWriter",
    model= Gemini(model="gemini-2.5-flash-lite"),
    instruction=load_instruction_from_file("scriptwriter_instruction.txt"),
    tools=[google_search],
    output_key="generated_script" # Save result to state
)

#-- Visualizer Sub Agent ---
visualizer_agent = Agent(
    name="ShortVisualizer",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction=load_instruction_from_file("visualizer_instruction.txt"),
    description="Generates visual concepts based on the provided script.",
    output_key="visual_concepts" # Save result to state
)

# Formatter Sub Agent
formatter_agent = Agent(
    name="ConceptFormatter",
    model=Gemini(model="gemini-2.5-flash-lite"),
    instruction=load_instruction_from_file("formatter_instruction.txt"),
    description="Formats the final Short concept.",
    output_key="final_shorts_concept" # Save result to state
)

# LLM Agent which uses the sub-agents
youtube_shorts_agent = SequentialAgent(
    name="YouTubeShortsAgent",
    sub_agents=[scriptwriter_agent, visualizer_agent, formatter_agent]
)

root_agent = youtube_shorts_agent
