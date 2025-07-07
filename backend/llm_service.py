import json
from typing import Optional, Dict, Any
from config import settings

class LLMService:
    def __init__(self):
        self.gemini_client = None
        self.openai_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize LLM clients based on available API keys"""
        # Initialize Gemini
        if settings.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self.gemini_client = genai.GenerativeModel('gemini-pro')
                print("Initialized Gemini client")
            except ImportError:
                print("Warning: google-generativeai not available")
            except Exception as e:
                print(f"Error initializing Gemini: {e}")
        
        # Initialize OpenAI (fallback)
        if settings.openai_api_key:
            try:
                import openai
                openai.api_key = settings.openai_api_key
                self.openai_client = openai
                print("Initialized OpenAI client")
            except ImportError:
                print("Warning: openai not available")
            except Exception as e:
                print(f"Error initializing OpenAI: {e}")
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate AI response using available LLM"""
        
        # Try Gemini first
        if self.gemini_client:
            try:
                return await self._generate_gemini_response(prompt, context)
            except Exception as e:
                print(f"Gemini error: {e}")
        
        # Try OpenAI as fallback
        if self.openai_client:
            try:
                return await self._generate_openai_response(prompt, context)
            except Exception as e:
                print(f"OpenAI error: {e}")
        
        # Fallback to mock response
        return self._generate_mock_response(prompt, context)
    
    async def _generate_gemini_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response using Gemini"""
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
            
            response = self.gemini_client.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"Gemini generation error: {e}")
            raise
    
    async def _generate_openai_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate response using OpenAI"""
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
            
            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. Provide accurate and helpful responses based on the context provided."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI generation error: {e}")
            raise
    
    def _generate_mock_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate mock response for development/testing"""
        if context:
            return f"Based on the provided context, here's what I can tell you about '{prompt}': This is a mock response since no LLM service is configured. In production, this would be a real AI-generated response based on your knowledge base."
        else:
            return f"Thank you for your question: '{prompt}'. This is a mock response since no LLM service is configured. Please set up your API keys to get real AI responses."
    
    def get_available_models(self) -> Dict[str, bool]:
        """Get status of available LLM models"""
        return {
            "gemini": self.gemini_client is not None,
            "openai": self.openai_client is not None,
            "mock": True  # Always available as fallback
        }

# Global LLM service instance
llm_service = LLMService() 