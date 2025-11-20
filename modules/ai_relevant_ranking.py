import dotenv
import os

from openai import OpenAI

dotenv.load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    print(
        """Error: OPENAI_API_KEY environment variable not set. Please copy the .env.template file as .env and fill it in.
    
    You can execute these commands in the terminal to get started:
    cp .env.template .env
    code .env
    """
    )

# Test OpenAI Access
print(
    OpenAI()
    .responses.create(
        model=os.environ["OPENAI_DEFAULT_MODEL"], input="Say: We are up and running!"
    )
    .output_text
)