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
    user_review_agent = Agent(
        name="User Review Analyzer",
        role="Analyze user reviews and feedback from similar products",
        model=OpenAIChat(id="gpt-4o"),
        tools=[GoogleSearch()],
        instructions=[
            "Search for user reviews of similar products/apps",
            "Identify common pain points and desired features",
            "Format findings as 'Theme: User Feedback'",
            "Include star ratings where available",
            "Focus on both positive and negative feedback",
            "Include direct user quotes when relevant",
            "Analyze reviews from multiple platforms (App Store, Play Store, ProductHunt, etc.)",
            "Each point should be on a new line starting with '-'",
            "Include source at the end of each point in square brackets"
        ],
        show_tool_calls=True,
        markdown=True,
    )

    competitor_analysis_agent = Agent(
        name="Competitor Analysis Expert",
        role="Analyze competing products and their features",
        model=OpenAIChat(id="gpt-4o"),
        tools=[GoogleSearch()],
        instructions=[
            "Identify top 5 competing products",
            "Compare pricing models and tiers",
            "List key features of each competitor",
            "Identify unique selling propositions",
            "Note user satisfaction scores",
            "Include download/user numbers where available",
            "Present data in clear tables"
        ],
        show_tool_calls=True,
        markdown=True,
    )

    user_persona_agent = Agent(
        name="User Persona Developer",
        role="Create detailed user personas based on market research",
        model=OpenAIChat(id="gpt-4o"),
        tools=[GoogleSearch()],
        instructions=[
            "Identify 3-4 key user personas",
            "For each persona include:",
            "- Demographics",
            "- Goals and motivations",
            "- Pain points",
            "- Feature preferences",
            "- Willingness to pay",
            "- Usage patterns",
            "Base personas on real market data and user feedback"
        ],
        show_tool_calls=True,
        markdown=True,
    )

    feature_pricing_agent = Agent(
        name="Feature & Pricing Strategist",
        role="Analyze desired features and optimal pricing strategies",
        model=OpenAIChat(id="gpt-4o"),
        tools=[GoogleSearch()],
        instructions=[
            "Analyze most requested features",
            "Recommend feature prioritization",
            "Suggest pricing tiers based on user feedback",
            "Include willingness to pay data",
            "Compare with competitor pricing",
            "Recommend monetization strategy",
            "Include market-specific pricing considerations"
        ],
        show_tool_calls=True,
        markdown=True,
    )

    market_fit_agent = Agent(
        name="Product-Market Fit Analyzer",
        role="Evaluate product-market fit and growth opportunities",
        model=OpenAIChat(id="gpt-4o"),
        tools=[GoogleSearch()],
        instructions=[
            "Analyze market demand signals",
            "Identify underserved user needs",
            "Evaluate competitive advantages",
            "Suggest product positioning",
            "Identify potential early adopters",
            "Recommend go-to-market strategy",
            "Include user acquisition channels"
        ],
        show_tool_calls=True,
        markdown=True,
    )
    
    return user_review_agent, competitor_analysis_agent, user_persona_agent, feature_pricing_agent, market_fit_agent

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
    if not any(prefix in content for prefix in ['content=', '\nRunning:', 'messages=[Message']):
        return content
        
    # Extract content between tool execution blocks
    if "\nRunning:" in content:
        parts = content.split("\nRunning:")
        # Get the last part after all tool executions
        for part in parts:
            if "\n\n" in part:
                content = part.split("\n\n", 1)[1]
    
    # Remove content= wrapper if present
    if 'content="' in content:
        content = content.split('content="')[1].split('"')[0]
    
    # Remove any remaining system messages
    if "messages=[Message" in content:
        content = content.split("messages=[Message")[0]
    
    # Clean up any remaining special characters and extra whitespace
    content = content.replace("\\n", "\n").strip()
    
    return content

def display_agent_response(agent_name, content):
    """Display the agent response with proper formatting."""
    st.subheader(f"🔍 {agent_name}")
    
    # Clean the content
    cleaned_content = clean_agent_response(content)
    
    # If content contains a table, format it properly
    if '|' in cleaned_content:
        # Split into text and table sections
        sections = cleaned_content.split('\n\n')
        for section in sections:
            if '|' in section:
                # Ensure table has proper markdown formatting
                lines = section.split('\n')
                if len(lines) >= 2:  # Valid table needs at least header and separator
                    # Format table with proper spacing
                    formatted_lines = []
                    for i, line in enumerate(lines):
                        if '|' in line:
                            cells = line.split('|')
                            formatted_cells = [''] + [cell.strip() for cell in cells if cell.strip()] + ['']
                            formatted_lines.append('|'.join(formatted_cells))
                            # Add separator after header
                            if i == 0:
                                separator = '|' + '|'.join(['---' for _ in range(len(formatted_cells)-2)]) + '|'
                                formatted_lines.append(separator)
                    
                    st.markdown('\n'.join(formatted_lines))
            else:
                # Display non-table content
                st.markdown(section)
    else:
        # Display regular text content
        st.markdown(cleaned_content)
    
    st.markdown("---")

def run_analysis(business_type, progress_bar, status_text):
    user_review_agent, competitor_analysis_agent, user_persona_agent, feature_pricing_agent, market_fit_agent = initialize_agents()
    
    agent_outputs = []
    progress_step = 0.2
    
    try:
        # User Review Analysis
        status_text.text("Analyzing user reviews...")
        review_prompt = f"Find and analyze user reviews for apps/products similar to {business_type}"
        review_response = user_review_agent.run(review_prompt)
        agent_outputs.append(("User Review Analysis", str(review_response)))
        progress_bar.progress(progress_step)

        # Competitor Analysis
        status_text.text("Analyzing competitors...")
        competitor_prompt = f"Analyze top competing products in the {business_type} space"
        competitor_response = competitor_analysis_agent.run(competitor_prompt)
        agent_outputs.append(("Competitor Analysis", str(competitor_response)))
        progress_bar.progress(progress_step * 2)

        # User Personas
        status_text.text("Developing user personas...")
        persona_prompt = f"Create user personas for {business_type} based on market research"
        persona_response = user_persona_agent.run(persona_prompt)
        agent_outputs.append(("User Personas", str(persona_response)))
        progress_bar.progress(progress_step * 3)

        # Feature & Pricing Analysis
        status_text.text("Analyzing features and pricing...")
        pricing_prompt = f"Analyze desired features and optimal pricing for {business_type}"
        pricing_response = feature_pricing_agent.run(pricing_prompt)
        agent_outputs.append(("Feature & Pricing Analysis", str(pricing_response)))
        progress_bar.progress(progress_step * 4)

        # Product-Market Fit
        status_text.text("Evaluating product-market fit...")
        fit_prompt = f"Evaluate product-market fit for {business_type}"
        fit_response = market_fit_agent.run(fit_prompt)
        agent_outputs.append(("Product-Market Fit", str(fit_response)))
        progress_bar.progress(1.0)
        
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
