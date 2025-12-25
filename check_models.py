import google.generativeai as genai
import os

# PASTE YOUR KEY HERE DIRECTLY FOR THE TEST
GOOGLE_API_KEY = "AIzaSyD-KgW98cOwR_8TIwSsUndpELiAZtfX6qI"
genai.configure(api_key=GOOGLE_API_KEY)

print("Checking available models for your API key...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")