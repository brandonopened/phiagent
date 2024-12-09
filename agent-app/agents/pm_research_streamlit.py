import streamlit as st
import pandas as pd
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.googlesearch import GoogleSearch
from phi.tools.yfinance import YFinanceTools
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
import re
import os
import base64
from io import BytesIO

# Initialize agents
def initialize_agents():
    web_agent = Agent(
        name="Web Agent",
        role="Search the web for latest information and news",
        model=OpenAIChat(id="gpt-4o"),
        tools=[GoogleSearch()],
        instructions=[
            "Your agent will now:",
            "Search for latest news and information about the given topic",
            "Format each finding as 'Key Development: Details'",
            "Include only the most relevant 3-5 developments",
            "Always include sources",
            "Use tables to display data",
            "Integrate market, technology, and organizational perspectives",
            "Focus on both value creation and value capture",
            "Include actionable recommendations",
            "Each point should be on a new line starting with '-'",
            "Include source at the end of each point in square brackets"
        ],
        show_tool_calls=True,
        markdown=True,
    )

    finance_agent = Agent(
        name="Finance Agent",
        role="Analyze financial data and market trends",
        model=OpenAIChat(id="gpt-4o"),
        tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
        instructions=[
            "Analyze financial metrics and market data",
            "Present data in clear tables",
            "Highlight key financial insights and trends"
        ],
        show_tool_calls=True,
        markdown=True,
    )

    tech_market_agent = Agent(
        name="Technology and Market Opportunity Expert",
        role="Analyze technology trends, market dynamics, and identify value creation opportunities",
        model=OpenAIChat(id="gpt-4o"),
        tools=[GoogleSearch()],
        instructions=[
            "Provide a structured market analysis with these specific sections:",
            
            "1. MARKET SIZE & GROWTH",
            "- Current global market size with specific dollar amount",
            "- Year-over-year growth rate (CAGR)",
            "- 5-year market size projection",
            "- Break down by major geographic regions",
            
            "2. MARKET SEGMENTS",
            "- List top 3-5 market segments with size/share",
            "- Identify fastest growing segments",
            "- Key drivers for each segment",
            
            "3. COMPETITIVE LANDSCAPE",
            "- Market share of top 5 players",
            "- Recent funding rounds and valuations",
            "- Key partnerships and acquisitions",
            
            "4. GROWTH DRIVERS & TRENDS",
            "- List specific technological advancements",
            "- Regulatory impacts",
            "- Customer demand patterns"
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
            "Include source at the end of each point in square brackets"
        ],
        show_tool_calls=True,
        markdown=True,
    )
    
    return web_agent, finance_agent, tech_market_agent, value_capture_agent, org_design_agent

def display_table(df):
    """Display a formatted table using Streamlit."""
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

def clean_agent_response(raw_response):
    """Extract clean content from agent response."""
    content = raw_response
    
    # If content is already clean, return it
    if not any(prefix in content for prefix in ['content=', '\nRunning:', 'messages=[Message', 'get_']):
        return content
    
    # Extract the main content after all tool executions
    if "\nRunning:" in content:
        parts = content.split("\nRunning:")
        # Get the last meaningful part
        for part in parts:
            if "\n\n" in part and "|" in part:  # Look for table content
                content = part.split("\n\n", 1)[1]
                break
    
    # Remove content= wrapper if present
    if 'content="' in content:
        content = content.split('content="')[1].split('"')[0]
    
    # Clean up any remaining special characters and extra whitespace
    content = (content.replace("\\n", "\n")
              .replace("```", "")
              .replace("markdown", "")
              .strip())
    
    # Format tables properly
    if "|" in content:
        lines = content.split("\n")
        formatted_lines = []
        in_table = False
        
        for line in lines:
            line = line.strip()
            if "|" in line:
                # Clean up table formatting
                cells = [cell.strip() for cell in line.split("|")]
                cells = [cell for cell in cells if cell]  # Remove empty cells
                formatted_line = "| " + " | ".join(cells) + " |"
                formatted_lines.append(formatted_line)
                
                # Add separator after header if not present
                if not in_table:
                    separator = "|" + "|".join(" --- " for _ in cells) + "|"
                    formatted_lines.append(separator)
                    in_table = True
            else:
                if line:  # Only add non-empty lines
                    formatted_lines.append(line)
                    in_table = False
        
        content = "\n".join(formatted_lines)
    
    return content

def display_agent_response(agent_name, content):
    """Display the agent response with proper formatting."""
    st.subheader(f"🔍 {agent_name}")
    
    # Clean and format the content
    cleaned_content = clean_agent_response(content)
    
    # Split content into sections
    sections = cleaned_content.split("\n\n")
    
    for section in sections:
        if section.strip():  # Only process non-empty sections
            if "|" in section:
                # It's a table - ensure proper markdown formatting
                st.markdown(section)
                st.markdown("---")  # Add separator after table
            else:
                # Regular text content
                st.markdown(section)
    
    st.markdown("---")  # Add final separator

def run_analysis(business_type, progress_bar, status_text):
    web_agent, finance_agent, tech_market_agent, value_capture_agent, org_design_agent = initialize_agents()
    
    agent_outputs = []
    progress_step = 0.2  # Changed from 100/5 to 0.2 (20% per step)
    
    try:
        # Web Agent
        status_text.text("Gathering latest news...")
        web_prompt = f"Provide latest news and developments in the {business_type} industry"
        web_response = web_agent.run(web_prompt)
        agent_outputs.append(("Industry News", str(web_response)))
        progress_bar.progress(progress_step)

        # Tech Market Agent
        status_text.text("Analyzing market...")
        market_prompt = f"Based on the above news, provide detailed market analysis for {business_type} industry"
        market_response = tech_market_agent.run(market_prompt)
        agent_outputs.append(("Market Analysis", str(market_response)))
        progress_bar.progress(progress_step * 2)

        # Finance Agent
        status_text.text("Analyzing financials...")
        finance_prompt = f"Analyze financial metrics of key players in the {business_type} industry"
        finance_response = finance_agent.run(finance_prompt)
        agent_outputs.append(("Financial Analysis", str(finance_response)))
        progress_bar.progress(progress_step * 3)

        # Value Capture Agent
        status_text.text("Developing strategies...")
        value_prompt = f"Develop strategic recommendations for entering the {business_type} market"
        value_response = value_capture_agent.run(value_prompt)
        agent_outputs.append(("Strategic Recommendations", str(value_response)))
        progress_bar.progress(progress_step * 4)

        # Org Design Agent
        status_text.text("Designing organization...")
        org_prompt = f"Propose organizational structure for a {business_type} company"
        org_response = org_design_agent.run(org_prompt)
        agent_outputs.append(("Organizational Design", str(org_response)))
        progress_bar.progress(1.0)  # Changed from 100 to 1.0
        
        return agent_outputs
        
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="Business Analysis System", layout="wide")
    
    # Sidebar
    with st.sidebar:
        st.title("🏢 Business Analysis System")
        st.markdown("---")
        
        business_type = st.text_input("What kind of company do you want to analyze?")
        generate_button = st.button("Generate Analysis")
        
        with st.expander("ℹ️ How to use"):
            st.markdown("""
            1. Enter the type of business you want to analyze
            2. Click 'Generate Analysis' to start
            3. View comprehensive analysis including:
               - Industry News
               - Market Analysis
               - Financial Analysis
               - Strategic Recommendations
               - Organizational Design
            """)

    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            if isinstance(message["content"], pd.DataFrame):
                display_table(message["content"])
            else:
                st.markdown(message["content"])
    
    if generate_button:
        if not business_type:
            st.sidebar.warning("Please enter a business type")
            return
            
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        agent_outputs = run_analysis(business_type, progress_bar, status_text)
        
        if agent_outputs:
            for agent_name, output in agent_outputs:
                with st.chat_message("assistant"):
                    display_agent_response(agent_name, output)
                    
                # Add to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": (agent_name, clean_agent_response(output))
                })
            
            progress_bar.empty()
            status_text.text("Analysis complete!")

if __name__ == "__main__":
    main()
