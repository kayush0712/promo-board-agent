# backend/agents/base.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import json
import time
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv
from models import ReviewSession

load_dotenv()

ENV = os.environ.get("ENV")


OLLAMA_MODELS = {
    "small":  os.environ.get("OLLAMA_MODEL_SMALL",  "llama3.2"),
    "medium": os.environ.get("OLLAMA_MODEL_MEDIUM", "qwen2.5:7b"),
    "large":  os.environ.get("OLLAMA_MODEL_LARGE",  "qwen2.5:14b"),
}

GROQ_MODELS = {
    "small":  "llama-3.1-8b-instant",
    "medium": "llama-3.3-70b-versatile",
    "large":  "llama-3.3-70b-versatile",
}


if ENV == "production":
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    print(f"Using Groq")
else:
    client = OpenAI(
        base_url = "http://localhost:11434/v1",
        api_key  = "ollama"
    )
    print(f"Using Ollama")


def call_llm(
    system_prompt: str,
    user_prompt:   str,
    agent_name:    str,
    session:       ReviewSession,
    temperature:   float = 0.2,
    max_tokens:    int   = 3000,
    model_size:    str   = "medium"   
) -> str:

    if ENV == "production":
        model = GROQ_MODELS.get(model_size, GROQ_MODELS["medium"])
    else:
        model = OLLAMA_MODELS.get(model_size, OLLAMA_MODELS["medium"])

    MAX_RETRIES = 3

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model       = model,   
                messages    = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt}
                ],
                temperature = temperature,
                max_tokens  = max_tokens
            )

            finish_reason = response.choices[0].finish_reason
            if finish_reason == "length":
                print(f"[{agent_name}] Response truncated — increase max_tokens")

            session.tokens.add(
                agent_name    = agent_name,
                input_tokens  = response.usage.prompt_tokens,
                output_tokens = response.usage.completion_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            error_msg = str(e)

            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                if "tokens per day" in error_msg.lower():
                    raise Exception(f"[{agent_name}] Daily token limit exhausted.")
                wait = 2 ** attempt
                print(f"Rate limit hit. Waiting {wait}s before retry {attempt + 1}/{MAX_RETRIES}")
                time.sleep(wait)
                continue

            if "connection refused" in error_msg.lower():
                raise Exception(f"[{agent_name}] Cannot connect")

            if attempt == MAX_RETRIES - 1:
                raise Exception(f"[{agent_name}] Failed after {MAX_RETRIES} attempts: {error_msg}")

            continue

    raise Exception(f"[{agent_name}] All retries exhausted")

def sanitize_text(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    return text.replace("<", "").replace(">", "")
    
def parse_json(raw: str, agent_name: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    print(f"[{agent_name}] Could not parse JSON. Raw output:\n{raw}")
    return {
        "error":   True,
        "agent":   agent_name,
        "raw":     raw[:500],
        "message": "Failed to parse LLM response as JSON"
    }


if __name__ == "__main__":
    from models import ReviewSession

    print("\n=== Test 1: Basic LLM Call ===")
    session = ReviewSession("TEST")

    response = call_llm(
        system_prompt = "You are a helpful assistant. Always reply in one sentence.",
        user_prompt   = "What is 2 + 2?",
        agent_name    = "test_agent",
        session       = session,
        model_size    = "small"   # test with small model
    )
    print(f"Response: {response}")
    print(f"Tokens:   {session.tokens.records}")

    print("\n=== Test 2: Model Sizes ===")
    for size in ["small", "medium", "large"]:
        if ENV == "production":
            print(f"  {size:8} → {GROQ_MODELS[size]}")
        else:
            print(f"  {size:8} → {OLLAMA_MODELS[size]}")

    print("\n=== Test 3: JSON Parsing ===")
    clean   = '{"decision": "RECOMMEND", "confidence": 88}'
    wrapped = '```json\n{"decision": "HOLD", "confidence": 45}\n```'
    buried  = 'Analysis: {"decision": "RECOMMEND", "confidence": 72} Done.'
    broken  = "I think the employee deserves promotion."

    print(f"Clean:   {parse_json(clean, 'test')}")
    print(f"Wrapped: {parse_json(wrapped, 'test')}")