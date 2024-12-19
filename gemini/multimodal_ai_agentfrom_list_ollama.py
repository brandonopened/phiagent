
from phi.agent import Agent
from phi.model.ollama import Ollama 
from phi.tools.duckduckgo import DuckDuckGo
import time

# 1. Initialize the Multimodal Agent
agent = Agent(model=Ollama(id="llama3.2-vision:11b"), markdown=True)

def web_search(query, max_results=3):
    try:
        results = ddg(query, max_results=max_results)
        return [{'title': r['title'], 'link': r['link'], 'snippet': r['body']} for r in results]
    except Exception as e:
        print(f"Search error: {e}")
        return []

# 2. Image Input
image_url = "image.jpg"

# 3. Audio Input
audio_file = "audio.mp3"

# 4. Video Input
video_file = "video.mp4"  # Direct path to video file

# 5. Multimodal Query
query = """ 
Analyze the inputs:
1. **Image**: Describe the scene and its significance.  
2. **Audio**: Extract key messages that relate to the visual.  
3. **Video**: Look at the video input and provide insights that connect with the image and audio context.  

For any significant objects, landmarks, or concepts identified:
- Search for additional context and relevant information
- Include found information in the analysis

Summarize the overall theme or story these inputs convey, enriched with the discovered context.
"""

# 6. Process media and perform searches
response = agent.run(query, images=[image_url], audio=audio_file, videos=[video_file])

# Extract key elements for search
search_terms = agent.run("List the main objects, landmarks, or concepts identified in the media that should be researched further:", 
                        images=[image_url], audio=audio_file, videos=[video_file])

# Perform searches and compile additional context
search_results = []
for term in search_terms.split('\n'):
    if term.strip():
        results = web_search(term)
        search_results.extend(results)

# 7. Generate final response with enriched context
final_query = f"""
Based on the initial analysis and these additional findings:
{search_results}

Provide a comprehensive analysis that incorporates both the direct media analysis and the discovered context.
"""

agent.print_response(final_query, images=[image_url], audio=audio_file, videos=[video_file], stream=True)