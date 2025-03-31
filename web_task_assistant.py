from google import genai
import requests
from bs4 import BeautifulSoup
import json

# Initialize the Gemini client
client = genai.Client(api_key="add_your_api_key_here")

def interpret_task(task_description):
    """Use Gemini to interpret the web task and determine the website to visit"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Given this task: '{task_description}', provide a JSON response with these fields: 'website_url' (the most appropriate website URL to visit), 'extraction_targets' (list of data elements to extract), 'search_query' (if applicable). Format as valid JSON only.",
    )
    
    # Parse the JSON response
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        # If Gemini doesn't return valid JSON, try to extract it
        response_text = response.text
        if '{' in response_text and '}' in response_text:
            json_str = response_text[response_text.find('{'):response_text.rfind('}')+1]
            return json.loads(json_str)
        return {"error": "Could not parse response", "raw_response": response.text}

def fetch_webpage(url):
    """Fetch the content of a webpage"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    return response.text

def extract_information(html_content, extraction_targets, task_description):
    """Use Gemini to extract the relevant information from the webpage"""
    # Create a simplified version of the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract text content to reduce token usage
    page_text = soup.get_text(separator='\n', strip=True)
    
    # Limit text to avoid token limits
    if len(page_text) > 10000:
        page_text = page_text[:10000] + "..."
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"""
Task: {task_description}
Extraction targets: {', '.join(extraction_targets)}
Webpage content:
{page_text}

Extract the requested information from the webpage content above. Format your response as JSON with keys matching the extraction targets.
""",
    )
    
    # Parse the JSON response
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        # If Gemini doesn't return valid JSON, try to extract it
        response_text = response.text
        if '{' in response_text and '}' in response_text:
            # Find the first opening brace and last closing brace
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            json_str = response_text[start:end]
            
            # Try to parse the extracted JSON
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # If still failing, try a more aggressive approach to clean the JSON
                import re
                # Try to find a valid JSON object using regex
                json_pattern = r'(\{.*\})'
                matches = re.findall(json_pattern, response_text, re.DOTALL)
                
                if matches:
                    for potential_json in matches:
                        try:
                            return json.loads(potential_json)
                        except json.JSONDecodeError:
                            continue
                
                # If all attempts fail, return the error
                return {"error": "Could not parse response", "raw_response": response.text}
        return {"error": "Could not parse response", "raw_response": response.text}

def execute_web_task(task_description):
    """Main function to execute a web task using Gemini"""
    print(f"Interpreting task: {task_description}")
    
    # Step 1: Interpret the task
    task_info = interpret_task(task_description)
    
    if "error" in task_info:
        return task_info
    
    print(f"Navigating to: {task_info['website_url']}")
    
    # Step 2: Fetch the webpage
    html_content = fetch_webpage(task_info['website_url'])
    
    # Step 3: Extract information
    print(f"Extracting information: {task_info['extraction_targets']}")
    result = extract_information(html_content, task_info['extraction_targets'], task_description)
    
    return result

def save_results_to_file(result, task_description, filename=None):
    """Save the extracted information to a text file in the current folder"""
    if filename is None:
        # Create a filename based on the task description
        # Replace spaces with underscores and remove special characters
        import re
        safe_task = re.sub(r'[^\w\s]', '', task_description)
        safe_task = safe_task.replace(' ', '_')[:30]  # Limit length
        filename = f"{safe_task}_results.txt"
    
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(f"Task: {task_description}\n")
        file.write(f"Timestamp: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if "error" in result:
            file.write(f"Error: {result['error']}\n")
            if "raw_response" in result:
                file.write(f"\nRaw Response:\n{result['raw_response']}\n")
        else:
            file.write("Extracted Information:\n")
            for key, value in result.items():
                if isinstance(value, list):
                    file.write(f"\n{key}:\n")
                    for i, item in enumerate(value, 1):
                        if isinstance(item, dict):
                            file.write(f"  {i}.\n")
                            for k, v in item.items():
                                file.write(f"    {k}: {v}\n")
                        else:
                            file.write(f"  {i}. {item}\n")
                else:
                    file.write(f"\n{key}: {value}\n")
    
    print(f"Results saved to {filename}")
    return filename

# Example usage
if __name__ == "__main__":
    # Get task description from user input
    print("Web Task Assistant")
    print("------------------")
    task = input("Enter your web task (e.g., 'Find the top 5 AI related headlines'): ")
    
    if not task:
        task = "Find the top 5 AI related headlines from a reputable tech news site"
        print(f"Using default task: {task}")
    
    # Execute the web task
    result = execute_web_task(task)
    print("\nExtracted Information:")
    print(json.dumps(result, indent=2))
    
    # Save results to a text file
    save_results_to_file(result, task)



