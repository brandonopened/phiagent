from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.tools.googlesearch import GoogleSearch
from phi.tools.yfinance import YFinanceTools
from phi.playground import Playground, serve_playground_app


browser_use_agent = Agent(
    name="Browser-Use Agent",
    role="Assist users with browser-based tasks and provide web-based information",
    model=OpenAIChat(id="gpt-4o"),
    tools=[GoogleSearch()],
    instructions=[
        "Perform browser-based tasks as requested by the user.",
        "Provide accurate and relevant information retrieved from the web.",
        "Ensure responses are concise and include references where applicable.",
    ],
    show_tool_calls=True,
    markdown=True,
    debug_mode=True,
)




# Define individual agents
web_agent = Agent(
    name="Web Agent",
    role="Search the web for information",
    model=OpenAIChat(id="gpt-4o"),
    tools=[GoogleSearch()],
    instructions=[
        "Given a topic by the user, respond with 4 latest news items about that topic.",
        "Search for 10 news items and select the top 4 unique items.",
        "Search in English and in French.",
    ],
    show_tool_calls=True,
    markdown=True,
    debug_mode=True,
)

finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
    instructions=["Use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)

tech_market_agent = Agent(
    name="Technology and Market Opportunity Expert",
    role="Analyze technology trends, market dynamics, and identify value creation opportunities",
    model=OpenAIChat(id="gpt-4o"),
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
    model=OpenAIChat(id="gpt-4o"),
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
    model=OpenAIChat(id="gpt-4o"),
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

app = Playground(agents=[
    browser_use_agent,
    finance_agent, 
    web_agent, 
    tech_market_agent, 
    value_capture_agent, 
    org_design_agent
]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)
