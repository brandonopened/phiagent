from phidata.agent import Agent
from phidata.model.ollama import Ollama
from phidata.tools.googlesearch import GoogleSearch
from phidata.tools.yfinance import YFinanceTools
import inspect
import types

# Define individual agents with Ollama - removing tools from the model configuration
web_agent = Agent(
    name="Web Agent",
    role="Search the web for information",
    model=Ollama(id="llama2:13b"),
    tools=[GoogleSearch()],
    instructions=["Always include sources"],
    show_tool_calls=True,
    markdown=True,
)

finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    model=Ollama(id="llama2:13b"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
    instructions=["Use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)

tech_market_agent = Agent(
    name="Technology and Market Opportunity Expert",
    role="Analyze technology trends, market dynamics, and identify value creation opportunities",
    model=Ollama(id="llama2:13b"),
    tools=[GoogleSearch()],
    instructions=[
        "Analyze emerging technology trends and market dynamics",
        "Identify potential market opportunities",
        "Evaluate competitive landscapes",
        "Always include data-driven insights",
        "Always include sources"
    ],
    show_tool_calls=True,
    markdown=True,
)

value_capture_agent = Agent(
    name="Value Capture Strategist",
    role="Develop strategies for IP protection, market positioning, and competitive advantage",
    model=Ollama(id="llama2:13b"),
    tools=[GoogleSearch()],
    instructions=[
        "Focus on IP protection strategies",
        "Develop market positioning recommendations",
        "Identify competitive advantages",
        "Provide actionable strategic recommendations",
        "Always include sources"
    ],
    show_tool_calls=True,
    markdown=True,
)

org_design_agent = Agent(
    name="Organizational Design Architect",
    role="Design optimal organizational structures and collaboration networks",
    model=Ollama(id="llama2:13b"),
    tools=[GoogleSearch()],
    instructions=[
        "Design team structures and collaboration frameworks",
        "Optimize for innovation and value delivery",
        "Consider organizational culture and dynamics",
        "Provide practical implementation steps",
        "Always include sources"
    ],
    show_tool_calls=True,
    markdown=True,
)

# Combine agents into a team
agent_team = Agent(
    team=[
        web_agent, 
        finance_agent, 
        tech_market_agent, 
        value_capture_agent, 
        org_design_agent
    ],
    instructions=[
        "Always include sources",
        "Use tables to display data",
        "Provide comprehensive product management strategies",
        "Integrate market, technology, and organizational perspectives",
        "Focus on both value creation and value capture",
        "Include actionable recommendations"
    ],
    show_tool_calls=True,
    markdown=True,
)

def inspect_function(func):
    if callable(func):
        if isinstance(func, types.BuiltinFunctionType):
            print("Cannot inspect signature of built-in type.")
        else:
            try:
                argspec = inspect.signature(func)
                print(f"Signature: {argspec}")
            except ValueError:
                print("Signature could not be retrieved.")
    else:
        raise ValueError("Provided object is not callable.")

def start_business_analysis():
    business_type = input("What kind of company do you want to create? ")
    prompt = f"Analyze the opportunities, challenges, and strategies for creating a company focused on '{business_type}'. Provide comprehensive recommendations on market positioning, financial planning, technology trends, organizational design, and value capture."
    agent_team.print_response(prompt, stream=True)

if __name__ == "__main__":
    start_business_analysis()