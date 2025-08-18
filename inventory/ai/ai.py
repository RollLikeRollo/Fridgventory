from io import BytesIO
import os
import pprint as pp
from typing import List
import json

from django.db.models import QuerySet
from django.http import FileResponse, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Google Gemini imports
from google import genai
from google.genai import types

from inventory.models import Item





def _get_prompt_for_language(language: str) -> str:
    """Load the appropriate prompt file based on language."""
    if language == "cs":
        prompt_file = "prompts/cs_consumtion_analysis.txt"
    else:
        prompt_file = "prompts/en_consumtion_analysis.txt"
    
    try:
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to a basic prompt if file doesn't exist
        return """
        Based on the inventory and consumed items, identify which items should be removed from inventory.
        Return a JSON response with the following format:
        {
            "consumed_items": [
                {
                    "item_id": 1,
                    "item_name": "item_name",
                    "missing_quantity": 10
                }
            ]
        }
        """


def _call_ollama_api(prompt: str) -> str:
    """Call Ollama API with the given prompt."""
    OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
    
    payload = {
        "model": os.getenv("OLLAMA_MODEL", "llama3"),
        "prompt": prompt,
        "stream": False,
    }
    
    print("Calling Ollama with payload:")
    pp.pp(payload)
    
    response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
    response.raise_for_status()
    
    raw_response = response.json()['response']
    print(10*"=" + "ollama_response" + 10*"=")
    pp.pp(raw_response)
    
    return raw_response


def _call_gemini_api(prompt: str) -> str:
    """Call Gemini API with the given prompt."""
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        print(f"Calling Gemini model: {model}")
        print("Prompt:")
        print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
        
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking
            ),
        )
        
        raw_response = response.text
        print(10*"=" + "gemini_response" + 10*"=")
        pp.pp(raw_response)
        
        return raw_response
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        raise


def _parse_llm_response(raw_response: str) -> list:
    """Parse the LLM response and extract consumed items."""
    try:
        llm_suggestions = json.loads(raw_response)
        return llm_suggestions.get("consumed", [])
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {raw_response}")
        
        # Try to extract JSON from the response if it's wrapped in other text
        import re
        json_match = re.search(r'\{[\s\S]*\}', raw_response)
        if json_match:
            try:
                llm_suggestions = json.loads(json_match.group())
                return llm_suggestions.get("consumed", [])
            except json.JSONDecodeError:
                pass
            
        # Try to add matching parentheses and brackets to the response
        json_match = re.search(r'\{[\s\S]*\}', raw_response)
        if json_match:
            try:
                llm_suggestions = json.loads(json_match.group())
                return llm_suggestions.get("consumed", [])
            except json.JSONDecodeError:
                pass
            
        
        return []


@csrf_exempt
@require_POST
def get_consumed_suggestions(request):
    """
    Receives user input about consumed items and uses an LLM
    to suggest inventory items for deletion.
    Supports both Ollama and Gemini APIs based on MODEL_PROVIDER env var.
    """
    try:
        data = json.loads(request.body)
        user_input = data.get("userInput")
        if not user_input:
            return JsonResponse({"error": "No user input provided."}, status=400)

        # Get the current inventory as a simple, structured list
        current_inventory = list(Item.objects.all().values('id', 'name', 'current_quantity'))
        
        # Load the appropriate prompt based on language
        language = data.get("language", "en")
        base_prompt = _get_prompt_for_language(language)
        
        # Craft the complete prompt
        full_prompt = base_prompt + f"""
        
        # Here is my current inventory:
        {json.dumps(current_inventory)}
        
        # Here is the speech of the worker from which you extract the items to be removed from the inventory:
        {user_input}
        """

        # Determine which AI provider to use
        model_provider = os.getenv("MODEL_PROVIDER", "ollama").lower()
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            # Call the appropriate API
            func_llm = None
            if model_provider == "gemini":
                func_llm = _call_gemini_api
            elif model_provider == "ollama":
                func_llm = _call_ollama_api
            else:
                return JsonResponse({
                    "error": f"Unsupported MODEL_PROVIDER: {model_provider}. Use 'ollama' or 'gemini'."
                }, status=400)
            
            raw_response = func_llm(full_prompt)

            # Parse the response
            items_llm = _parse_llm_response(raw_response)
            print(f"DEBUG: raw_response = {raw_response}")
            print(f"DEBUG: items_llm = {items_llm}, type = {type(items_llm)}")
            
            if items_llm and isinstance(items_llm, list):
                break
            
            retry_count += 1
            print(f"LLM returned an unparseable response (attempt {retry_count}/{max_retries}): {raw_response}")
            

        # Check if we exhausted retries or got valid data
        if not items_llm or not isinstance(items_llm, list):
            print(f"ERROR: Failed to get valid response after {max_retries} attempts. items_llm = {items_llm}, type: {type(items_llm)}")
            return JsonResponse({"error": "AI failed to provide valid response after multiple attempts"}, status=500)
        
        # Fetch the actual Item objects from the database
        item_ids = []
        for item_llm in items_llm:
            if isinstance(item_llm, dict) and "id" in item_llm:
                item_ids.append(item_llm.get("id"))
        
        suggested_items = Item.objects.filter(id__in=item_ids)
        
        # Create a mapping of item_id to consumed quantity from AI response
        consumed_map = {}
        for item_llm in items_llm:
            if isinstance(item_llm, dict) and "id" in item_llm and "consumed" in item_llm:
                consumed_map[item_llm.get("id")] = item_llm.get("consumed", 0)

        response_data = [
            {
                "id": item.id, 
                "name": item.name, 
                "consumed": consumed_map.get(item.id, 0)
            }
            for item in suggested_items
        ]

        return JsonResponse({"suggestions": response_data})

    except Exception as e:
        print(f"Error in get_consumed_suggestions: {e}")
        return JsonResponse({"error": str(e)}, status=500)