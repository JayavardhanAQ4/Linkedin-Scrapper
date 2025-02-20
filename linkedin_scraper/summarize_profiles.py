import json
from langchain_ollama import OllamaLLM  
from langchain_core.prompts import ChatPromptTemplate

model = OllamaLLM(model="llama3.2")

def generate_summary(profile_data):
    """Generate an AI-powered summary from profile data."""
    prompt = ChatPromptTemplate.from_template(
        "Summarize the following LinkedIn profile:\n{profile_data}\nKeep it concise and insightful."
    )
    formatted_profile = json.dumps(profile_data, indent=2)
    return model.invoke(prompt.format(profile_data=formatted_profile))

if __name__ == "__main__":
    with open("scraped_profiles.json", "r") as f:
        profiles = json.load(f)
    
    for profile in profiles:
        profile["summary"] = generate_summary(profile)
    
    with open("profile_summaries.json", "w") as f:
        json.dump(profiles, f, indent=4)
