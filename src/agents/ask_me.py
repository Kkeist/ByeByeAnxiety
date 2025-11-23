"""
Ask Me Agent - Specialized learning assistant for ADHD-friendly knowledge exploration
"""
import railtracks as rt
from typing import Optional
from datetime import datetime


class AskMeAgent:
    """AI agent specialized in breaking down complex topics for ADHD learners"""
    
    def __init__(self, llm_provider: str = "gemini", api_key: str = "", 
                 custom_instructions: str = ""):
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.custom_instructions = custom_instructions
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the Railtracks agent with appropriate LLM"""
        
        # Base system message optimized for ADHD learning
        base_system_message = """You are Ask Me, a specialized learning assistant designed to help individuals with ADHD understand complex topics.

Core Teaching Principles:
- Start with the ANSWER FIRST, then explain the details
- Break complex topics into small, digestible chunks
- Use clear, simple language without being condescending
- Provide concrete examples and analogies
- Keep paragraphs short (2-3 sentences max)
- Use bullet points and numbered lists frequently
- Explain the "why" behind concepts, not just the "what"
- Be patient with repeated questions
- Encourage curiosity and exploration

Response Structure:
1. Quick Answer (1-2 sentences): Give the core answer immediately
2. Essential Explanation (3-5 short paragraphs): Break down the key concepts
3. Deeper Details (optional): Only if the user wants to go deeper

Communication Style:
- Direct and clear
- Enthusiastic about learning
- Non-judgmental
- Encouraging of questions
- Comfortable with tangents and follow-ups

Remember:
- ADHD learners often need to understand WHY something works to grasp HOW it works
- Breaking things down is not "dumbing down" - it's making knowledge accessible
- Every question is valid and worth answering
- Jumping between topics is natural - embrace it"""

        if self.custom_instructions:
            base_system_message += f"\n\nCustom Instructions:\n{self.custom_instructions}"
        
        # Select LLM based on provider
        if self.llm_provider == "gemini":
            llm = rt.llm.GeminiLLM("gemini-2.5-flash", api_key=self.api_key)
        else:  # anthropic/claude
            llm = rt.llm.AnthropicLLM("claude-3-5-sonnet-20241022", api_key=self.api_key)
        
        # Create the agent (no tools needed for Ask Me)
        self.agent = rt.agent_node(
            name="Ask Me",
            llm=llm,
            system_message=base_system_message
        )
    
    async def ask(self, question: str, conversation_history: Optional[list] = None) -> str:
        """
        Ask a question and get an ADHD-friendly explanation.
        
        Args:
            question: The user's question
            conversation_history: Optional previous messages in this conversation
        
        Returns:
            Agent's response
        """
        if conversation_history:
            # Build message history for context
            messages = []
            for msg in conversation_history:
                if msg['role'] == 'user':
                    messages.append(rt.llm.UserMessage(msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(rt.llm.AssistantMessage(msg['content']))
            # Add current question
            messages.append(rt.llm.UserMessage(question))
            response = await rt.call(self.agent, messages)
        else:
            response = await rt.call(self.agent, question)
        
        return response.text
    
    async def explain_like_adhd(self, topic: str) -> str:
        """
        Provide an ADHD-optimized explanation of a topic.
        
        Args:
            topic: Topic to explain
        
        Returns:
            ADHD-friendly explanation
        """
        prompt = f"""Explain this topic in an ADHD-friendly way: {topic}

Remember to:
1. Start with a quick, clear answer
2. Break it into small chunks
3. Explain WHY it matters
4. Use examples
5. Keep it engaging"""

        response = await rt.call(self.agent, prompt)
        return response.text
    
    async def break_down_concept(self, concept: str) -> str:
        """
        Break down a complex concept into its fundamental parts.
        
        Args:
            concept: Concept to break down
        
        Returns:
            Broken down explanation
        """
        prompt = f"""Break down this concept into its most basic parts: {concept}

Structure your response as:
1. Core Idea (one sentence)
2. Key Components (bullet points)
3. How It Works (step by step)
4. Why It Matters (practical relevance)

Keep each section short and clear."""

        response = await rt.call(self.agent, prompt)
        return response.text
    
    def update_instructions(self, new_instructions: str):
        """Update custom instructions and reinitialize agent"""
        self.custom_instructions = new_instructions
        self._initialize_agent()
    
    def update_api_key(self, api_key: str, provider: str):
        """Update API key and provider"""
        self.api_key = api_key
        self.llm_provider = provider
        self._initialize_agent()

