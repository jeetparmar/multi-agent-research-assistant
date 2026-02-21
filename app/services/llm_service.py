from openai import AsyncOpenAI
from app.core.config import settings

# Initialize the OpenAI client with the API key from settings
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Helper function to call the LLM with system and user prompts
async def call_llm(system_prompt: str, user_prompt: str):
    # Call the OpenAI API to get a response based on the provided prompts
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content
