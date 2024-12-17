from phi.agent import Agent
from phi.model.ollama import Ollama
import pandas as pd
import os

# Define the skill analysis agent
skill_analysis_agent = Agent(
    name="Skill Relevancy Analyzer",
    role="Analyze skills to determine if they are legitimate professional skills",
    model=Ollama(id="llama3.1:8b"),
    instructions=[
        "Determine if skills are legitimate professional competencies",
        "Identify real technologies, methodologies, and business practices",
        "Recognize standard industry terms and technologies",
        "Filter out non-professional or made-up skills",
    ],
    show_tool_calls=True,
    markdown=True,
)

def analyze_job_descriptions(title: str, description: str, all_skills_df) -> tuple[str, str]:
    """
    Analyze if skills are redundant and should be removed from taxonomy
    """
    try:
        analysis_prompt = f'''
        Review this skill: "{title}" ({description})
        
        Compare it to these related skills in our taxonomy:
        {all_skills_df[all_skills_df['title'].str.lower() != title.lower()][['title', 'description']].to_string()}

        If this skill is redundant with another skill or is less useful for a workforce skills taxonomy:
        1. Respond "remove" if it should be removed
        2. Respond "keep" if it should be kept

        Respond with ONLY "remove" or "keep".
        '''
        
        decision = skill_analysis_agent.run(
            analysis_prompt,
            stream=False
        )
        
        if isinstance(decision, str):
            return decision.strip().lower()
        return "keep"  # default to keeping if unsure
        
    except Exception as e:
        print(f"Error processing skill {title}: {str(e)}")
        return "error"

def read_csv_with_fallback(file_path):
    """Try different encodings to read the CSV file"""
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            print(f"Trying to read CSV with {encoding} encoding...")
            df = pd.read_csv(file_path, encoding=encoding)
            print("Columns found:", df.columns.tolist())  # Debug print
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error with {encoding}: {str(e)}")
            continue
    
    # If all attempts fail, try with the most permissive approach
    print("Attempting to read with unicode_escape encoding...")
    return pd.read_csv(file_path, encoding='unicode_escape')

def process_skills_csv():
    # Read the input CSV file
    input_csv_path = os.path.join(os.path.dirname(__file__), 'empath_all.csv')
    output_csv_path = os.path.join(os.path.dirname(__file__), 'empath_all_cleaned.csv')
    
    # Use the new reading function
    df = read_csv_with_fallback(input_csv_path)
    
    # Print column names for debugging
    print("Available columns:", df.columns.tolist())
    
    # Add new column for removal decisions if it doesn't exist
    if 'action' not in df.columns:
        df['action'] = ''
    
    # Process each skill
    for index, row in df.iterrows():
        print(f"\nAnalyzing skill: {row['title']}")
        try:
            action = analyze_job_descriptions(
                row['title'],
                row['description'],
                df
            )
            df.at[index, 'action'] = action
            
            # Save after each analysis in case of interruption, preserving all original columns
            df.to_csv(output_csv_path, index=False, encoding='utf-8', 
                     columns=['abbreviation', 'title', 'description', 'category', 'Keywords', 'action'])
            print(f"Result for {row['title']}: {action}")
        except Exception as e:
            print(f"Error analyzing {row['title']}: {str(e)}")
            df.at[index, 'action'] = "error"
            df.to_csv(output_csv_path, index=False, encoding='utf-8',
                     columns=['abbreviation', 'title', 'description', 'category', 'Keywords', 'action'])
    
    print("\nAnalysis complete! Results saved to empath_all_cleaned.csv")
    return df

if __name__ == "__main__":
    process_skills_csv()