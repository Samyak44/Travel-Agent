from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import sys
import os
import httpx
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.shared.config import get_settings

settings = get_settings()


class TravelAgent:
    """LangChain-powered travel agent"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.7,
            openai_api_key=settings.openai_api_key,
        )
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        self.conversations = {}  # Store conversation memories

    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent to use"""

        async def search_flights(query: str) -> str:
            """
            Search for flights based on user requirements.
            Query should include: origin, destination, dates, passengers, class.
            Example: "Search flights from NYC to London, departing 2024-03-15, 2 passengers, economy"
            """
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{settings.flight_service_url}/api/flights/search",
                        json={"query": query},
                        timeout=30.0,
                    )
                    return response.json()
            except Exception as e:
                return f"Error searching flights: {str(e)}"

        async def search_hotels(query: str) -> str:
            """
            Search for hotels based on user requirements.
            Query should include: city, check-in, check-out, guests, preferences.
            Example: "Search hotels in Paris, check-in 2024-03-15, check-out 2024-03-20, 2 guests, 4-star minimum"
            """
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{settings.hotel_service_url}/api/hotels/search",
                        json={"query": query},
                        timeout=30.0,
                    )
                    return response.json()
            except Exception as e:
                return f"Error searching hotels: {str(e)}"

        async def get_weather(query: str) -> str:
            """
            Get weather information for a location.
            Query should include: city name or coordinates, optional date range.
            Example: "Weather in Paris for next 5 days"
            """
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{settings.weather_service_url}/api/weather",
                        params={"query": query},
                        timeout=30.0,
                    )
                    return response.json()
            except Exception as e:
                return f"Error fetching weather: {str(e)}"

        return [
            Tool(
                name="search_flights",
                func=search_flights,
                description="Search for flights based on user requirements. Use this when the user wants to find flights, book tickets, or compare flight prices.",
            ),
            Tool(
                name="search_hotels",
                func=search_hotels,
                description="Search for hotels based on user requirements. Use this when the user wants to find accommodation, book hotels, or compare hotel prices.",
            ),
            Tool(
                name="get_weather",
                func=get_weather,
                description="Get weather information for a travel destination. Use this when the user asks about weather conditions, climate, or what to pack.",
            ),
        ]

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent"""

        system_message = """You are an expert AI travel agent assistant. Your role is to help users plan their trips by:

1. Understanding their travel needs and preferences
2. Asking clarifying questions to gather important details like:
   - Origin and destination
   - Travel dates
   - Number of passengers/guests
   - Budget preferences
   - Travel class preferences
   - Accommodation preferences
   - Special requirements or accessibility needs

3. Using available tools to search for:
   - Flights (search_flights)
   - Hotels (search_hotels)
   - Weather information (get_weather)

4. Providing personalized recommendations based on user preferences

5. Being conversational, friendly, and helpful

Important guidelines:
- Always ask for missing information before searching (dates, locations, etc.)
- Consider the user's budget and preferences
- Provide multiple options when possible
- Explain the benefits of different choices
- Be proactive in suggesting things users might not have considered
- Location is CRITICAL - always confirm exact cities and airports

Start by greeting the user and asking how you can help with their travel plans."""

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_openai_functions_agent(self.llm, self.tools, prompt)

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
        )

    def get_or_create_memory(self, conversation_id: str) -> ConversationBufferMemory:
        """Get or create conversation memory"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
            )
        return self.conversations[conversation_id]

    async def chat(
        self, message: str, conversation_id: str, user_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and return response

        Args:
            message: User message
            conversation_id: Unique conversation ID
            user_context: Optional user context (preferences, location, etc.)

        Returns:
            Response dict with message and metadata
        """
        try:
            memory = self.get_or_create_memory(conversation_id)

            # Add user context to the prompt if available
            if user_context:
                context_str = f"\n\nUser Context:\n"
                if user_context.get("preferences"):
                    context_str += f"Preferences: {user_context['preferences']}\n"
                if user_context.get("budget"):
                    context_str += f"Budget: {user_context['budget']}\n"
                message = message + context_str

            # Run the agent
            response = await self.agent.ainvoke(
                {
                    "input": message,
                    "chat_history": memory.chat_memory.messages,
                }
            )

            # Save to memory
            memory.chat_memory.add_user_message(message)
            memory.chat_memory.add_ai_message(response["output"])

            return {
                "message": response["output"],
                "conversation_id": conversation_id,
                "suggestions": self._extract_suggestions(response),
            }

        except Exception as e:
            return {
                "message": f"I apologize, but I encountered an error: {str(e)}. Could you please rephrase your question?",
                "conversation_id": conversation_id,
                "error": str(e),
            }

    def _extract_suggestions(self, response: Dict[str, Any]) -> List[str]:
        """Extract follow-up suggestions from response"""
        suggestions = [
            "Tell me more about flights",
            "Show me hotel options",
            "What's the weather like?",
            "Help me plan my itinerary",
        ]
        return suggestions[:3]

    def clear_conversation(self, conversation_id: str):
        """Clear conversation history"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
