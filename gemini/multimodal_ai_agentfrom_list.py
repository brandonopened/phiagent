from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
import pandas as pd

# 1. Load product images from CSV
products_df = pd.read_csv('products.csv')

# 2. Initialize the Multimodal Agent
agent = Agent(model=Gemini(id="gemini-2.0-flash-exp"), tools=[DuckDuckGo()], markdown=True)

# 3. Product Analysis Query
query = """ 
Analyze this product image and provide insights:
1. **Visual Analysis**: Describe the product's appearance, design, and key features visible in the image
2. **Web Search**: Find relevant information about:
   - Product reviews and ratings
   - Key features and specifications
   - Similar products in the market
   - Current market trends related to this product
3. Provide a comprehensive summary combining visual insights with web research.
"""

# 4. Loop through each product in the CSV
for index, row in products_df.iterrows():
    print(f"\n\n=== Analyzing Product {index + 1} ===\n")
    image_url = row['link']
    agent.print_response(query, images=[image_url], stream=True)

# Commented out video and audio processing
# audio_file = "audio.mp3"
# video_file = upload_file("video.mp4")  
# while video_file.state.name == "PROCESSING":  
#     time.sleep(2)
#     video_file = get_file(video_file.name)