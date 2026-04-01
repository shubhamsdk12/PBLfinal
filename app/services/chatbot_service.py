"""
Groq-powered chatbot service for intelligent financial assistance.
Uses Groq's LLM API with OpenAI-compatible interface.
"""
import httpx
import logging
from typing import Optional, List, Dict
from app.config import settings

logger = logging.getLogger(__name__)


class GroqChatbotService:
    """
    Service for AI-powered chatbot responses using Groq API.

    Features:
    - Personalized financial advice based on user data
    - Budget optimization suggestions
    - Investment pattern recommendations
    - Context-aware responses
    """

    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    SYSTEM_PROMPT = """You are a helpful financial assistant for a student budget management app called SpendWise.

Your role is to:
1. Provide personalized spending suggestions based on the user's financial data
2. Suggest investment patterns and when to save/invest
3. Give budget optimization advice
4. Answer financial questions intelligently
5. Alert users to potential budget risks

Guidelines:
- Be concise but helpful (responses should be 2-4 sentences typically)
- Use Indian Rupee (Rs.) for currency
- Be encouraging but realistic about budget constraints
- If the user asks about something unrelated to finance/budgeting, politely redirect to financial topics
- Reference specific numbers from their data when giving advice
- Do not make up financial data - only use what is provided in the context

Current User's Financial Context:
{user_context}
"""

    @staticmethod
    def _build_user_context(budget_info: dict) -> str:
        """
        Build a context string from budget info for the system prompt.

        Args:
            budget_info: Dictionary from get_budget_info()

        Returns:
            Formatted context string
        """
        budget_health = "Critical" if budget_info['remaining_budget'] < 0 else (
            "Low" if budget_info['remaining_budget'] < budget_info['monthly_budget'] * 0.2 else "Healthy"
        )

        return f"""
- Monthly Budget: Rs.{budget_info['monthly_budget']:.2f}
- Total Spent This Month: Rs.{budget_info['total_spent']:.2f}
- Remaining Budget: Rs.{budget_info['remaining_budget']:.2f}
- Today's Spending: Rs.{budget_info['today_spent']:.2f}
- Additional (Unplanned) Expenses: Rs.{budget_info['additional_spent']:.2f}
- Days Remaining in Budget Cycle: {budget_info['days_remaining']}
- Days Elapsed: {budget_info['days_elapsed']}
- Daily Allowance (if spread evenly): Rs.{budget_info['daily_allowance']:.2f}
- Investment Balance: Rs.{budget_info['investment_balance']:.2f}
- Budget Setup Complete: {budget_info['budget_setup_complete']}
- Budget Health: {budget_health}
"""

    @staticmethod
    async def get_groq_response(
        user_message: str,
        budget_info: dict,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Get AI response from Groq API.

        Args:
            user_message: The user's question/message
            budget_info: Dictionary containing user's financial data
            conversation_history: Optional list of previous messages for context

        Returns:
            AI-generated response string

        Raises:
            Exception: If API call fails
        """
        user_context = GroqChatbotService._build_user_context(budget_info)
        system_prompt = GroqChatbotService.SYSTEM_PROMPT.format(user_context=user_context)

        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            for msg in conversation_history[-6:]:
                messages.append(msg)

        messages.append({"role": "user", "content": user_message})

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": settings.GROQ_MODEL,
            "messages": messages,
            "max_tokens": settings.GROQ_MAX_TOKENS,
            "temperature": settings.GROQ_TEMPERATURE,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GroqChatbotService.GROQ_API_URL,
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                raise Exception(f"Groq API returned status {response.status_code}")

            data = response.json()

            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise Exception("Invalid response format from Groq API")

    @staticmethod
    def get_fallback_response(budget_info: dict) -> str:
        """
        Provide a fallback response when Groq API is unavailable.

        This ensures the chatbot always responds, even during outages.
        """
        if not budget_info["budget_setup_complete"]:
            return (
                "It looks like you haven't set up your budget yet! "
                "Please go to the Dashboard and set up your monthly budget first."
            )

        return (
            f"I'm currently experiencing technical difficulties, but here's your status:\n"
            f"- Remaining Budget: Rs.{budget_info['remaining_budget']:.2f}\n"
            f"- Days Left: {budget_info['days_remaining']}\n"
            f"- Daily Allowance: Rs.{budget_info['daily_allowance']:.2f}\n\n"
            f"Please try again in a moment."
        )
