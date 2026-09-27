"""
Gemini SDK Client Integration (google-genai).
"""

from __future__ import annotations

import logging
import os
import sys
import time
import warnings
from typing import Optional, Type, TypeVar

# Silence Google GenAI SDK AFC warnings
warnings.filterwarnings("ignore", message=".*Automatic function calling.*")
warnings.filterwarnings("ignore", message=".*Direct use of automatic function calling.*")
logging.getLogger("google.genai").setLevel(logging.ERROR)

from google import genai
from google.genai import errors, types
from pydantic import BaseModel

from student42.ai.tools import AgentToolRegistry
from student42.core.config import get_settings

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    """Wrapper around official google-genai client with retry and multi-model fallback."""

    FALLBACK_CHAIN = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is missing. Configure your .env file."
            )
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.primary_model = settings.gemini_primary_model
        self.fast_model = settings.gemini_fast_model

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None,
        use_fast_model: bool = False,
    ) -> T:
        """Calls Gemini enforcing a strict Pydantic JSON schema with retry and model fallback."""
        initial_model = self.fast_model if use_fast_model else self.primary_model
        candidate_models = [initial_model] + [m for m in self.FALLBACK_CHAIN if m != initial_model]

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_model,
            system_instruction=system_instruction,
            temperature=0.2,
        )

        last_error: Exception | None = None

        for model in candidate_models:
            for attempt in range(1, 3):
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=config,
                    )
                    if not response.text:
                        raise RuntimeError("Gemini returned an empty response.")
                    return response_model.model_validate_json(response.text)
                except errors.ServerError as e:
                    last_error = e
                    time.sleep(1.0 * attempt)
                except errors.ClientError as e:
                    last_error = e
                    if "404" in str(e):
                        break
                    raise

        raise RuntimeError(f"Gemini API unavailable across fallback models: {last_error}")

    def execute_agentic_loop(
        self,
        prompt: str,
        project_slug: str,
        system_instruction: str,
        max_tool_turns: int = 5,
    ) -> str:
        registry = AgentToolRegistry(project_slug)
        dispatch = registry.get_dispatch_map()
        tools = registry.get_tool_declarations()

        messages = [prompt]
        current_turn = 0

        while current_turn < max_tool_turns:
            current_turn += 1

            config = types.GenerateContentConfig(
                tools=tools,
                system_instruction=system_instruction,
                temperature=0.3,
            )

            response = self.client.models.generate_content(
                model=self.primary_model,
                contents=messages,
                config=config,
            )

            function_calls = response.function_calls
            if not function_calls:
                return response.text or "Analysis completed with no remarks."

            for call in function_calls:
                fn_name = call.name
                fn_args = call.args or {}

                if fn_name in dispatch:
                    tool_result = dispatch[fn_name](**fn_args)
                else:
                    tool_result = f"Error: Tool '{fn_name}' is not recognized."

                messages.append(
                    types.Content(
                        role="model",
                        parts=[types.Part.from_function_call(name=fn_name, args=fn_args)],
                    )
                )
                messages.append(
                    types.Content(
                        role="tool",
                        parts=[
                            types.Part.from_function_response(
                                name=fn_name,
                                response={"result": tool_result},
                            )
                        ],
                    )
                )

        return "Analysis halted: Maximum agent tool call depth reached."