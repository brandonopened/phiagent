from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
import pandas as pd
import atexit
import grpc

# 1. Load videos from CSV instead of products
videos_df = pd.read_csv('videos.csv')

# 2. Initialize the Multimodal Agent
agent = Agent(model=Gemini(id="gemini-2.0-flash-exp"), tools=[DuckDuckGo()], markdown=True)

# 3. Modified query for video analysis
query = """ 
Analyze this video and provide insights, specifically focusing on any mentions or references to 'Frog Street':
1. **Content Analysis**: 
   - Summarize the main content and purpose of the video
   - Note any explicit mentions of 'Frog Street' curriculum or materials
2. **Key Points**:
   - Educational concepts covered
   - Teaching methodologies shown
   - Any specific Frog Street materials or resources featured
3. Provide a brief summary highlighting Frog Street-related content if present.
"""

# 4. Loop through videos
for index, row in videos_df.iterrows():
    print(f"\n\n=== Analyzing Video {index + 1} ===\n")
    video_url = row['link']
    agent.print_response(query, images=[video_url], stream=True)

# Cleanup
def cleanup():
    # Properly shutdown gRPC
    try:
        grpc.aio.shutdown()  # For async gRPC
    except:
        pass  # Fallback if async shutdown fails

atexit.register(cleanup)