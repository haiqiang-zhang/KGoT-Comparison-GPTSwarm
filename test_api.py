import os
from openai import OpenAI
from dotenv import load_dotenv


def test_openai_api():
    # Initialize the OpenAI client
    load_dotenv(override=True)
    print(os.getenv('OPENAI_API_KEY'))
    print(os.getenv('OPENAI_ORGANIZATION'))
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    try:
        # Make a simple completion request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say 'Hello, API is working!'"}
            ]
        )
        
        # Print the response
        print("API Response:", response.choices[0].message.content)
        print("API test successful!")
        return True
        
    except Exception as e:
        print("Error testing API:", str(e))
        return False

if __name__ == "__main__":
    test_openai_api()
