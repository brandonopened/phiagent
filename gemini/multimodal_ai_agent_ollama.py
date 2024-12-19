from phi.agent import Agent
from phi.model.ollama import Ollama 
from phi.tools.duckduckgo import DuckDuckGo
import time

# 1. Initialize the Multimodal Agent
agent = Agent(model=Ollama(id="llama3.2-vision:11b"), markdown=True)

# 2. Image Input
image_url = "image.jpg"

# 3. Audio Input
audio_file = "audio.mp3"

# 4. Video Input
video_file = "video.mp4"  # Direct path to video file

# 5. Multimodal Query
query = """ 
Combine insights from the inputs:
1. **Image**: Describe the scene and its significance.  
2. **Audio**: Extract key messages that relate to the visual.  
3. **Video**: Look at the video input and provide insights that connect with the image and audio context.  
4. **Web Search**: Find the latest updates or events linking all these topics.
Summarize the overall theme or story these inputs convey.
"""

# 6. Multimodal Agent generates unified response
agent.print_response(query, images=[image_url], audio=audio_file, videos=[video_file], stream=True)