"""
Gemini SDK Client Integration (google-genai).
"""

from __future__ import annotations

import time
from typing import Optional, Type, TypeVar

from google import genai
from google.genai import errors, types
from pydantic import BaseModel

from student42.ai.tools import AgentToolRegistry
from student42.core.config import get_settings

T = TypeVar("T", bound=BaseModel)


class GeminiClient:
    """Wrapper around official google-genai client."""

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
        """Calls Gemini enforcing a strict Pydantic JSON schema with retry fallback."""
        model = self.fast_model if use_fast_model else self.primary_model

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_model,
            system_instruction=system_instruction,
            temperature=0.2,
        )

        # Retry logic for 503 temporary demand spikes
        attempts = 0
        last_error: Exception | None = None
        while attempts < 3:
            attempts += 1
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
                time.sleep(1.5 * attempts)
            except errors.ClientError as e:
                # If model is not found, attempt fallback to gemini-2.0-flash
                if "404" in str(e) and model != "gemini-2.0-flash":
                    model = "gemini-2.0-flash"
                    continue
                raise

        raise RuntimeError(f"Gemini API temporarily unavailable after retries: {last_error}")