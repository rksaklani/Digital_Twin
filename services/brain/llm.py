"""
LLM service using local quantized model.
Supports llama.cpp for GGUF models.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, AsyncIterator
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMService:
    """Local LLM service using llama.cpp"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('models', {}).get('llm', {})
        self.llm = None
        self.router = None
        self.memory = None  # Will be set by memory system
        self.prompts = self._load_prompts()
        self.interrupted = False
    
    def _load_prompts(self) -> Dict[str, str]:
        """Load prompt templates"""
        prompts = {}
        prompt_dir = Path(__file__).parent / 'prompts'
        
        for prompt_file in ['system.txt', 'style.txt', 'safety.txt']:
            prompt_path = prompt_dir / prompt_file
            if prompt_path.exists():
                with open(prompt_path, 'r') as f:
                    prompts[prompt_file.replace('.txt', '')] = f.read()
            else:
                prompts[prompt_file.replace('.txt', '')] = ""
        
        return prompts
    
    async def initialize(self):
        """Initialize LLM model"""
        logger.info("Initializing LLM service...")
        
        try:
            # Try to use llama-cpp-python
            from llama_cpp import Llama
            
            model_path = self.config.get('model_path', './models/llama-3.1-8b-instruct-q4_k_m.gguf')
            
            if not Path(model_path).exists():
                logger.warning(f"Model file not found: {model_path}")
                logger.warning("LLM service will use fallback mode")
                return
            
            self.llm = Llama(
                model_path=model_path,
                n_ctx=self.config.get('n_ctx', 4096),
                n_batch=self.config.get('n_batch', 512),
                n_threads=self.config.get('n_threads', 8),
                n_gpu_layers=self.config.get('n_gpu_layers', 35),
                use_mmap=self.config.get('use_mmap', True),
                use_mlock=self.config.get('use_mlock', False),
                verbose=False,
            )
            
            logger.info(f"LLM model loaded: {model_path}")
        
        except ImportError:
            logger.warning("llama-cpp-python not available, using fallback")
        except Exception as e:
            logger.error(f"Failed to load LLM model: {e}")
            logger.warning("LLM service will use fallback mode")
    
    def set_router(self, router):
        """Set event router"""
        self.router = router
    
    def set_memory(self, memory):
        """Set memory system"""
        self.memory = memory
    
    async def generate(self, user_input: str, intent: Optional[Dict[str, Any]] = None) -> str:
        """Generate response from user input"""
        self.interrupted = False
        
        # Build prompt
        prompt = self._build_prompt(user_input, intent)
        
        if not self.llm:
            # Fallback: simple rule-based response
            return self._fallback_response(user_input, intent)
        
        try:
            # Generate response
            response = await self._generate_streaming(prompt)
            
            # Store in memory
            if self.memory:
                await self.memory.add_exchange(user_input, response)
            
            return response
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error processing your request."
    
    def _build_prompt(self, user_input: str, intent: Optional[Dict[str, Any]]) -> str:
        """Build prompt from templates and context"""
        system_prompt = self.prompts.get('system', '')
        style_prompt = self.prompts.get('style', '')
        safety_prompt = self.prompts.get('safety', '')
        
        # Get conversation history
        history = ""
        if self.memory:
            history = self.memory.get_recent_history(max_turns=5)
        
        # Build full prompt
        prompt_parts = []
        
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}")
        
        if style_prompt:
            prompt_parts.append(f"Style: {style_prompt}")
        
        if safety_prompt:
            prompt_parts.append(f"Safety: {safety_prompt}")
        
        if history:
            prompt_parts.append(f"Conversation history:\n{history}")
        
        prompt_parts.append(f"User: {user_input}")
        prompt_parts.append("Assistant:")
        
        return "\n\n".join(prompt_parts)
    
    async def _generate_streaming(self, prompt: str) -> str:
        """Generate response with streaming"""
        if not self.llm:
            return ""
        
        # Run generation in executor to avoid blocking
        loop = asyncio.get_event_loop()
        
        def _generate():
            response_text = ""
            stream = self.llm(
                prompt,
                max_tokens=self.config.get('max_tokens', 256),
                temperature=self.config.get('temperature', 0.7),
                top_p=self.config.get('top_p', 0.9),
                top_k=self.config.get('top_k', 40),
                repeat_penalty=self.config.get('repeat_penalty', 1.1),
                stream=True,
                stop=["User:", "\n\n"],
            )
            
            for token in stream:
                if self.interrupted:
                    break
                response_text += token['choices'][0]['text']
            
            return response_text.strip()
        
        response = await loop.run_in_executor(None, _generate)
        return response
    
    def _fallback_response(self, user_input: str, intent: Optional[Dict[str, Any]]) -> str:
        """Fallback response when LLM is not available"""
        intent_type = intent.get('intent', 'statement') if intent else 'statement'
        
        if intent_type == 'question':
            return "That's an interesting question. I'm still learning, so I may not have a complete answer."
        elif intent_type == 'command':
            return "I understand you'd like me to do something. I'm working on improving my capabilities."
        else:
            return "I hear you. Thanks for sharing that with me."
    
    async def interrupt(self):
        """Interrupt current generation"""
        self.interrupted = True
        logger.info("LLM generation interrupted")
    
    async def shutdown(self):
        """Shutdown LLM service"""
        if self.llm:
            del self.llm
        logger.info("LLM service shutdown")

