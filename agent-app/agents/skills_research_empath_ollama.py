from phidata.agent import Agent
from phidata.model.ollama import Ollama
from phidata.tools.googlesearch import GoogleSearch
import pandas as pd
import os

# Define the skill analysis agent
skill_analysis_agent = Agent(
    name="Skill Relevancy Analyzer",
    role="Analyze job descriptions to determine skill relevancy",
    model=Ollama(id="llama2:13b"),
    tools=[GoogleSearch()],
    instructions=[
        "Analyze job descriptions to determine if skills are currently relevant",
        "Look for specific mentions and applications of the skill",
        "Consider both exact matches and related terminology",
        "Evaluate the quality and credibility of sources",
    ],
    show_tool_calls=True,
    markdown=True,
)

def analyze_job_descriptions(skill_title: str, description: str) -> str:
    """
    Analyze job descriptions to determine if a skill is relevant in current job market
    """
    search_prompt = f'''
    Search for current job descriptions that require the skill: "{skill_title}" 
    defined as: "{description}". 
    Find at least 3 high-quality job postings from reputable companies.
    '''
    
    # Get search results
    results = skill_analysis_agent.print_response(
        search_prompt,
        stream=False,
        return_messages=True
    )

    # Analyze the search results
    analysis_prompt = f'''
    Based on the search results, determine if the skill "{skill_title}" is relevant 
    in current job postings. Consider:
    1. Were there at least 3 high-quality job postings mentioning this skill?
    2. Is the skill used in the way described: "{description}"?
    
    Respond with ONLY "relevant" or "not relevant".
    '''
    
    relevancy = skill_analysis_agent.print_response(
        analysis_prompt,
        stream=False,
        return_messages=True
    )
    
    # Extract just the relevancy determination
    return relevancy[-1].content.strip().lower()

def process_skills_csv():
    # Read the CSV file
    csv_path = os.path.join(os.path.dirname(__file__), 'empath_skills.csv')
    df = pd.read_csv(csv_path)
    
    # Process each skill
    for index, row in df.iterrows():
        print(f"\nAnalyzing skill: {row['skill_title']}")
        relevancy = analyze_job_descriptions(
            row['skill_title'],
            row['description']
        )
        df.at[index, 'relevancy'] = relevancy
        
        # Save after each analysis in case of interruption
        df.to_csv(csv_path, index=False)
        print(f"Result for {row['skill_title']}: {relevancy}")
    
    print("\nAnalysis complete! Results saved to CSV.")
    return df

if __name__ == "__main__":
    process_skills_csv()