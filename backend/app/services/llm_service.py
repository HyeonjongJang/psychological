"""
LLM Service for Natural Chatbot (G4).

Integrates with OpenAI GPT-4 for conversational personality assessment
and trait inference from natural dialogue.
"""

import json
from typing import List, Dict, AsyncGenerator, Optional
from openai import AsyncOpenAI

from ..config import settings
from ..core.mini_ipip6_data import TRAITS, TRAIT_NAMES


# System prompt for natural conversation
NATURAL_CONVERSATION_PROMPT = """You are a friendly and engaging conversational partner having a casual chat. Your goal is to get to know the person you're talking to through natural conversation, WITHOUT explicitly mentioning personality assessment or psychological evaluation.

## Conversation Guidelines:

1. **Opening**: Start with a warm, casual greeting and ask an open-ended question about their interests, recent experiences, or daily life.

2. **Topics to Naturally Explore** (weave these in organically):
   - Hobbies, interests, and how they spend free time
   - Social activities and relationships with friends/family
   - Work or study habits and approach to tasks
   - How they handle stress or challenging situations
   - Their thoughts on trying new things and experiences
   - Their values and what matters to them

3. **Conversation Style**:
   - Be genuinely curious and engaged
   - Share brief, relatable responses to build rapport
   - Ask thoughtful follow-up questions based on their answers
   - Keep a natural conversational flow - don't interrogate
   - Show empathy and active listening
   - Use a warm, friendly tone

4. **Important**:
   - NEVER mention personality, assessment, traits, or psychology
   - Keep responses concise (2-4 sentences usually)
   - Let the conversation flow naturally
   - After 10+ exchanges, you can naturally wind down the conversation

Remember: This is a genuine friendly conversation, not an interview."""


# Prompt for inferring personality traits from conversation
INFERENCE_PROMPT = """Analyze the following conversation and assess the participant's personality across the Big Six dimensions. Base your assessment ONLY on evidence from the conversation.

## Trait Definitions (Mini-IPIP6):

1. **Extraversion**: Social engagement, talkativeness, energy in social situations, enjoys being around others
2. **Agreeableness**: Warmth, cooperation, empathy, concern for others' feelings, tolerance
3. **Conscientiousness**: Organization, dependability, self-discipline, attention to detail, goal-directed behavior
4. **Neuroticism**: Tendency toward negative emotions, anxiety, mood swings, emotional reactivity
5. **Openness to Experience**: Curiosity, creativity, imagination, interest in ideas and new experiences
6. **Honesty-Humility**: Sincerity, fairness, modesty, lack of greed or desire for status/luxury

## Scoring Guidelines:
- Use a 1.0 to 7.0 scale (1=very low, 4=average, 7=very high)
- Only score traits where you have clear evidence from the conversation
- If insufficient evidence, give a moderate score (3.5-4.5) with "low" confidence
- Provide specific quotes or examples as evidence

## Conversation Transcript:
{conversation}

## Required Output Format (JSON):
{{
  "extraversion": {{"score": X.X, "confidence": "high|medium|low", "evidence": "specific evidence..."}},
  "agreeableness": {{"score": X.X, "confidence": "high|medium|low", "evidence": "specific evidence..."}},
  "conscientiousness": {{"score": X.X, "confidence": "high|medium|low", "evidence": "specific evidence..."}},
  "neuroticism": {{"score": X.X, "confidence": "high|medium|low", "evidence": "specific evidence..."}},
  "openness": {{"score": X.X, "confidence": "high|medium|low", "evidence": "specific evidence..."}},
  "honesty_humility": {{"score": X.X, "confidence": "high|medium|low", "evidence": "specific evidence..."}}
}}

Respond ONLY with the JSON object, no additional text."""


class LLMService:
    """Service for LLM-based natural conversation and personality inference."""

    def __init__(
        self,
        api_key: str = None,
        model: str = None
    ):
        """
        Initialize LLM service.

        Args:
            api_key: OpenAI API key (defaults to settings)
            model: Model to use (defaults to settings)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL

        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None

    def is_configured(self) -> bool:
        """Check if LLM service is properly configured."""
        return self.client is not None

    def get_system_prompt(self) -> str:
        """Get the system prompt for natural conversation."""
        return NATURAL_CONVERSATION_PROMPT

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 300
    ) -> str:
        """
        Generate a conversational response.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Generated response text
        """
        if not self.client:
            raise ValueError("LLM service not configured. Set OPENAI_API_KEY.")

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 300
    ) -> AsyncGenerator[str, None]:
        """
        Stream a conversational response.

        Args:
            messages: Conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Yields:
            Response text chunks
        """
        if not self.client:
            raise ValueError("LLM service not configured. Set OPENAI_API_KEY.")

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def analyze_personality(
        self,
        conversation: List[Dict[str, str]]
    ) -> Dict:
        """
        Analyze conversation to infer personality traits.

        Args:
            conversation: Full conversation history

        Returns:
            Dict with trait scores and evidence
        """
        if not self.client:
            raise ValueError("LLM service not configured. Set OPENAI_API_KEY.")

        # Format conversation as transcript
        transcript = self._format_transcript(conversation)

        # Create inference prompt
        prompt = INFERENCE_PROMPT.format(conversation=transcript)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a personality psychology expert. Analyze conversations and provide trait assessments in JSON format only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for consistent analysis
            max_tokens=1000,
        )

        # Parse JSON response
        content = response.choices[0].message.content.strip()

        # Try to extract JSON if there's extra text
        if content.startswith("```"):
            # Remove markdown code blocks
            content = content.replace("```json", "").replace("```", "").strip()

        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # Return default moderate scores if parsing fails
            result = {
                trait: {
                    "score": 4.0,
                    "confidence": "low",
                    "evidence": "Unable to parse LLM response"
                }
                for trait in TRAITS
            }

        return result

    def _format_transcript(self, conversation: List[Dict[str, str]]) -> str:
        """
        Format conversation history as readable transcript.

        Args:
            conversation: List of message dicts with role and content

        Returns:
            Formatted transcript string
        """
        lines = []
        for msg in conversation:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            if role == "assistant":
                lines.append(f"Assistant: {content}")
            elif role == "user":
                lines.append(f"Participant: {content}")
            # Skip system messages in transcript

        return "\n".join(lines)

    def validate_inference_result(self, result: Dict) -> Dict:
        """
        Validate and normalize inference result.

        Ensures all traits are present with valid scores.

        Args:
            result: Raw inference result

        Returns:
            Validated and normalized result
        """
        validated = {}

        for trait in TRAITS:
            if trait in result:
                trait_data = result[trait]
                score = trait_data.get("score", 4.0)
                confidence = trait_data.get("confidence", "low")
                evidence = trait_data.get("evidence", "No evidence provided")

                # Clamp score to valid range
                score = max(1.0, min(7.0, float(score)))

                # Validate confidence
                if confidence not in ["high", "medium", "low"]:
                    confidence = "low"

                validated[trait] = {
                    "score": score,
                    "confidence": confidence,
                    "evidence": evidence,
                }
            else:
                # Default for missing traits
                validated[trait] = {
                    "score": 4.0,
                    "confidence": "low",
                    "evidence": "Insufficient evidence in conversation",
                }

        return validated


# Module-level instance
llm_service = LLMService()
