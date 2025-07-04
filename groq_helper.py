#!/usr/bin/env python3
"""
GroqHelper - Written by Arda Akgur

Uses Groq API with llama-3.3-70b-versatile model to classify text as save-worthy or not.
"""

import os
import asyncio
from groq import AsyncGroq  # pip install groq

class GroqHelper:
    def __init__(self, api_key=None, model="llama-3.3-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = AsyncGroq(api_key=self.api_key)
        self.model = model

    async def is_save_worthy(self, content: str) -> bool:
        """Returns True if model decides content is valuable to save, False otherwise."""
        prompt = (
            "You are an AI that helps decide if website content is worth storing "
            "for a knowledge base. Respond with only 'YES' if it is relevant and "
            "valuable, or 'NO' if it is trivial, off-topic, or unnecessary.\n\n"
            f"Content:\n{content[:2000]}"  # limit to first 2000 chars
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            answer = response.choices[0].message.content.strip().upper()
            return answer.startswith("YES")
        except Exception as e:
            print(f"[!] Groq API error: {e}")
            return False
