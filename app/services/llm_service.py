from groq import AsyncGroq
from app.core.config import settings

# Initialize the Groq client with the API key from settings
client = AsyncGroq(api_key=settings.GROQ_API_KEY)

# Helper function to call the LLM with system and user prompts
async def call_llm(system_prompt: str, user_prompt: str):
    # Call the Groq API to get a response based on the provided prompts
    response = await client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content or ""
