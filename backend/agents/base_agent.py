import httpx
import json
import logging
import re
import os
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BaseAgent")

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Clients and URLs
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def clean_json_response(text: str) -> str:
    """
    Cleans typical LLM markdown wrapper tags (like ```json ... ```) from the response text.
    """
    text = text.strip()
    # Remove markdown code blocks if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    return text

async def call_groq_fallback(client: httpx.AsyncClient, system_prompt: str, user_prompt: str, temperature: float, response_format: str = None) -> str:
    logger.info("Triggering Groq Llama-3 backup fallback...")
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature
    }
    if response_format == "json":
        payload["response_format"] = {"type": "json_object"}
        
    try:
        response = await client.post(GROQ_URL, headers=headers, json=payload)
        if response.status_code != 200:
            logger.error(f"Groq API fallback error {response.status_code}: {response.text}")
            raise ValueError(f"Groq API returned status code {response.status_code}: {response.text}")
            
        data = response.json()
        if "choices" not in data or len(data["choices"]) == 0:
            logger.error(f"Invalid Groq response format: {data}")
            raise ValueError(f"Invalid response from Groq: {data}")
            
        content = data["choices"][0]["message"]["content"]
        logger.info("Groq Llama-3.3 fallback successfully generated a response.")
        return content
    except Exception as e:
        logger.error(f"Failed to communicate with Groq API: {str(e)}")
        raise e

async def call_openrouter(
    model: str,
    system_prompt: str,
    user_prompt: str,
    api_key: str = None,
    temperature: float = 0.2,
    response_format: str = None
) -> str:
    """
    Makes an asynchronous POST request to the OpenRouter API, with Groq Llama-3 fallback.
    """
    api_key = api_key or OPENROUTER_API_KEY
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://inforge.ai", # Required by OpenRouter
        "X-Title": "InForge AI Data Platform",
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature
    }
    
    if response_format == "json":
        payload["response_format"] = {"type": "json_object"}
        
    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            logger.info(f"Calling OpenRouter model {model}...")
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            if response.status_code != 200:
                logger.warning(f"OpenRouter API returned status {response.status_code}. Attempting Groq fallback...")
                return await call_groq_fallback(client, system_prompt, user_prompt, temperature, response_format)
            
            data = response.json()
            if "choices" not in data or len(data["choices"]) == 0:
                logger.warning("Invalid OpenRouter response format. Attempting Groq fallback...")
                return await call_groq_fallback(client, system_prompt, user_prompt, temperature, response_format)
                
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"OpenRouter communication failed: {str(e)}. Attempting Groq fallback...")
            try:
                return await call_groq_fallback(client, system_prompt, user_prompt, temperature, response_format)
            except Exception as groq_err:
                logger.error(f"Both OpenRouter and Groq fallback failed! Groq error: {str(groq_err)}")
                raise e

async def call_openrouter_json(
    model: str,
    system_prompt: str,
    user_prompt: str,
    api_key: str = None,
    temperature: float = 0.2
) -> dict:
    """
    Helper to call OpenRouter and automatically parse the response as a JSON dictionary.
    """
    res_text = await call_openrouter(model, system_prompt, user_prompt, api_key=api_key, temperature=temperature)
    cleaned = clean_json_response(res_text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from response: {cleaned}. Error: {str(e)}")
        # Try to find something that looks like JSON inside
        bracket_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
        if bracket_match:
            try:
                return json.loads(bracket_match.group(1))
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Could not parse valid JSON from LLM response: {res_text}")

async def call_groq(
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    response_format: str = None,
    is_fallback: bool = False
) -> str:
    """
    Makes a direct asynchronous POST request to the Groq API.
    Uses the configured GROQ_API_KEY.
    Falls back to Gemini if Groq fails or is rate-limited.
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": temperature
    }
    if response_format == "json":
        payload["response_format"] = {"type": "json_object"}

    async with httpx.AsyncClient(timeout=90.0) as client:
        try:
            logger.info(f"Calling Groq model {model}...")
            response = await client.post(GROQ_URL, headers=headers, json=payload)
            if response.status_code != 200:
                logger.error(f"Groq API error {response.status_code}: {response.text}")
                raise ValueError(f"Groq API returned status code {response.status_code}: {response.text}")

            data = response.json()
            if "choices" not in data or len(data["choices"]) == 0:
                logger.error(f"Invalid Groq response format: {data}")
                raise ValueError(f"Invalid response from Groq: {data}")

            content = data["choices"][0]["message"]["content"]
            logger.info(f"Groq {model} successfully generated a response.")
            return content
        except Exception as e:
            if not is_fallback:
                logger.warning(f"Groq API failed: {str(e)}. Attempting Gemini fallback...")
                try:
                    return await call_gemini("gemini-2.0-flash-lite", system_prompt, user_prompt, temperature, is_fallback=True)
                except Exception as gemini_err:
                    logger.error(f"Both Groq and Gemini fallback failed! Gemini error: {str(gemini_err)}")
                    raise e
            else:
                logger.error(f"Failed to communicate with Groq API (fallback mode): {str(e)}")
                raise e

async def call_groq_json(
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    is_fallback: bool = False
) -> dict:
    """
    Helper to call Groq and automatically parse the response as a JSON dictionary.
    Falls back to Gemini JSON if Groq fails.
    """
    try:
        res_text = await call_groq(model, system_prompt, user_prompt, temperature, response_format="json", is_fallback=is_fallback)
        cleaned = clean_json_response(res_text)
        return json.loads(cleaned)
    except Exception as e:
        if not is_fallback:
            logger.warning(f"Groq JSON execution failed: {str(e)}. Attempting Gemini JSON fallback...")
            try:
                return await call_gemini_json("gemini-2.0-flash-lite", system_prompt, user_prompt, temperature, is_fallback=True)
            except Exception as gemini_err:
                logger.error(f"Both Groq and Gemini JSON fallback failed! Gemini error: {str(gemini_err)}")
                if 'cleaned' in locals():
                    bracket_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
                    if bracket_match:
                        try:
                            return json.loads(bracket_match.group(1))
                        except json.JSONDecodeError:
                            pass
                raise e
        else:
            if 'cleaned' in locals():
                bracket_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
                if bracket_match:
                    try:
                        return json.loads(bracket_match.group(1))
                    except json.JSONDecodeError:
                        pass
            raise e

async def call_gemini(
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    is_fallback: bool = False
) -> str:
    """
    Makes a call to the Google Gemini API using the new google.genai SDK.
    Falls back to Groq if Gemini is exhausted/rate-limited.
    """
    try:
        logger.info(f"Calling Gemini model {model_name}...")
        response = gemini_client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature
            )
        )
        
        content = response.text
        logger.info(f"Gemini {model_name} successfully generated a response.")
        return content
    except Exception as e:
        if not is_fallback:
            logger.warning(f"Gemini API failed: {str(e)}. Attempting Groq fallback...")
            try:
                return await call_groq("llama-3.3-70b-versatile", system_prompt, user_prompt, temperature, is_fallback=True)
            except Exception as groq_err:
                logger.error(f"Both Gemini and Groq fallback failed! Groq error: {str(groq_err)}")
                raise e
        else:
            logger.error(f"Failed to communicate with Gemini API (fallback mode): {str(e)}")
            raise e

async def call_gemini_json(
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    is_fallback: bool = False
) -> dict:
    """
    Helper to call Gemini and automatically parse the response as a JSON dictionary.
    Falls back to Groq JSON if Gemini fails.
    """
    try:
        res_text = await call_gemini(model_name, system_prompt, user_prompt, temperature, is_fallback=is_fallback)
        cleaned = clean_json_response(res_text)
        return json.loads(cleaned)
    except Exception as e:
        if not is_fallback:
            logger.warning(f"Gemini JSON execution failed: {str(e)}. Attempting Groq JSON fallback...")
            try:
                return await call_groq_json("llama-3.3-70b-versatile", system_prompt, user_prompt, temperature, is_fallback=True)
            except Exception as groq_err:
                logger.error(f"Both Gemini and Groq JSON fallback failed! Groq error: {str(groq_err)}")
                if 'cleaned' in locals():
                    bracket_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
                    if bracket_match:
                        try:
                            return json.loads(bracket_match.group(1))
                        except json.JSONDecodeError:
                            pass
                raise e
        else:
            if 'cleaned' in locals():
                bracket_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
                if bracket_match:
                    try:
                        return json.loads(bracket_match.group(1))
                    except json.JSONDecodeError:
                        pass
            raise e

