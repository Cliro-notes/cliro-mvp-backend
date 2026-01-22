import os 
from google import genai

# Gemini API Key Configuration
client = genai.Client(api_key="AIzaSyBr7Tu84ZBtWIqWDbDoVIiSLYb6M83Upf8")

# Prompt Template Function
def prompt_to_ai(userActionJSON: str) -> str:
    # Prompt para generar el output para el usuario
    prompt = f"""
        You are an AI assistant that modifies or analyzes text based on a user-selected action. In which the user provides a JSON object with the following structure:
        ACTION: Describes the operation to perform on the USER TEXT. Possible values include:
            - 'Resumir': Return a concise and clear summary preserving the original meaning.
            - 'Explicar': Explain the text clearly and simply, adapting the explanation level if PAYLOAD specifies it.
            - 'Reescribir': Rewrite the text while preserving meaning.
            - 'Traducir': Translate the text to the language specified in PAYLOAD.
        PAYLOAD (optional, may be null): If PAYLOAD specifies a tone or style, apply it consistently.
        USER TEXT: The text to be processed according to the ACTION and PAYLOAD.
        ---
        INSTRUCTIONS:
        - Perform the task strictly according to the selected ACTION.
        - If PAYLOAD is provided, use it as a modifier for the ACTION (e.g. tone, language, style, level of detail).
        - If PAYLOAD is null or empty, infer a reasonable default for the ACTION.
        - Do NOT explain what you are doing unless the ACTION explicitly requires explanation.
        - Do NOT add meta commentary, headers, or emojis.
        - Keep the output clean, direct, and useful.
        ---
        User JSON:
        {userActionJSON}
        OUTPUT ONLY THE RESULTING TEXT.
    """
    return prompt

# Output Function
def generate_ai_response(userActionJSON: str) -> str:
    prompt = prompt_to_ai(userActionJSON)
    # AI gets the prompt and generates the response
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )
    return response.text