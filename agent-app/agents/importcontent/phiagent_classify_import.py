import os
import base64
import json
import requests
import fitz  # PyMuPDF
from PIL import Image
import shutil
import pandas as pd

def check_existing_images(output_folder):
    """Check if folder exists and contains PNG images."""
    if not os.path.exists(output_folder):
        return False
    
    image_files = [f for f in os.listdir(output_folder) 
                   if f.endswith('.png') and f.startswith('page_')]
    return len(image_files) > 0

def pdf_to_images(pdf_path, output_folder):
    # Check if images already exist
    if check_existing_images(output_folder):
        print(f"Found existing images in {output_folder}, skipping PDF conversion...")
        return [os.path.join(output_folder, f) for f in sorted(os.listdir(output_folder)) 
                if f.endswith('.png') and f.startswith('page_')]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf = fitz.open(pdf_path)
    image_paths = []

    for page_num in range(len(pdf)):
        page = pdf[page_num]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_path = os.path.join(output_folder, f'page_{page_num + 1}.png')
        img.save(img_path)
        image_paths.append(img_path)

    pdf.close()
    print(f"Conversion complete. Images saved in {output_folder}")
    return image_paths

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def classify_image_with_ollama(image_path):
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    
    classification_prompt = """
    Analyze this image and classify it into one of these categories:
    1. Title Page
    2. Table of Contents
    3. Section Header
    4. Content Page with Tables
    5. Content Page with Lists
    6. Content Page with Paragraphs
    7. Forms or Worksheets
    8. Charts or Diagrams
    9. Other

    Provide your response in this exact format:
    CATEGORY: [category number and name]
    CONFIDENCE: [high/medium/low]
    REASONING: [brief explanation]
    """

    base64_image = encode_image(image_path)
    
    data = {
        "model": "llama3.2-vision:11b",
        "prompt": classification_prompt,
        "stream": False,
        "images": [base64_image]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        
        # Extract category from response
        response_text = result["response"]
        category = "other"  # default category
       
        # Parse the category from the response
        for line in response_text.split('\n'):
            if line.startswith('CATEGORY:'):
                category = line.split(':')[1].strip().lower()
                category = category.split('.')[0].strip()  # Get just the number
                break
                    
        return category
        
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return "error"

def organize_images_by_type(image_folder):
    categories = {
        "1": "title_pages",
        "2": "table_of_contents",
        "3": "section_headers",
        "4": "content_tables",
        "5": "content_lists",
        "6": "content_paragraphs",
        "7": "forms_worksheets",
        "8": "charts_diagrams",
        "9": "other"
    }
    
    # Create category directories
    for category in categories.values():
        category_path = os.path.join(image_folder, category)
        if not os.path.exists(category_path):
            os.makedirs(category_path)
    
    # Process each image
    results = []
    for filename in sorted(os.listdir(image_folder)):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, filename)
            
            # Skip if the file is in a category folder
            if any(category in image_path for category in categories.values()):
                continue
                
            print(f"Classifying {filename}...")
            category_num = classify_image_with_ollama(image_path)
            
            if category_num in categories:
                category_folder = categories[category_num]
                destination = os.path.join(image_folder, category_folder, filename)
                shutil.move(image_path, destination)
                print(f"Moved {filename} to {category_folder}")
            else:
                print(f"Could not classify {filename}, leaving in root folder")

            results.append({
                "file": filename,
                "category": categories.get(category_num, "other")
            })

    # Save the results to a spreadsheet
    df = pd.DataFrame(results)
    df.to_excel("pdf_page_classification.xlsx", index=False)

def main():
    pdf_path = 'datasample.pdf'  # Your PDF file
    base_output_folder = 'classified_pages'
    
    # First check and convert PDF to images if needed
    print("Checking for existing images...")
    image_paths = pdf_to_images(pdf_path, base_output_folder)
    
    # Then organize images into categories if needed
    print("\nChecking for existing classifications...")
    organize_images_by_type(base_output_folder)
    
    print("\nProcessing complete! Images have been organized into categories.")

if __name__ == "__main__":
    main()