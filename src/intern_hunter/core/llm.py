import groq
import google.generativeai as genai
import ollama
from intern_hunter.config import settings

class LLMEngine:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.ollama_model = settings.OLLAMA_MODEL
        
        self.groq_client = None
        if settings.GROQ_API_KEY:
            self.groq_client = groq.Groq(api_key=settings.GROQ_API_KEY)
            
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')

    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.5) -> str:
        """
        Generates text using the configured provider (groq, gemini, or ollama).
        """
        if self.provider == "ollama":
            return self._generate_ollama(prompt, system_prompt, temperature)
        elif self.provider == "gemini":
            return self._generate_gemini(prompt, system_prompt, temperature)
        else:
            return self._generate_groq(prompt, system_prompt, temperature)

    def _generate_groq(self, prompt: str, system_prompt: str, temperature: float) -> str:
        if not self.groq_client:
            return "Groq API key not configured."
            
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            res = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                temperature=temperature
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            return f"Groq Error: {str(e)}"

    def _generate_gemini(self, prompt: str, system_prompt: str, temperature: float) -> str:
        if not hasattr(self, 'gemini_model'):
            return "Gemini API key not configured."
            
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        try:
            res = self.gemini_model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(temperature=temperature)
            )
            return res.text.strip()
        except Exception as e:
            return f"Gemini Error: {str(e)}"

    def _generate_ollama(self, prompt: str, system_prompt: str, temperature: float) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = ollama.chat(
                model=self.ollama_model,
                messages=messages,
                options={'temperature': temperature}
            )
            return response['message']['content'].strip()
        except Exception as e:
            return f"Ollama Error: {str(e)}"

_llm_engine_instance = None

def get_llm_client() -> LLMEngine:
    global _llm_engine_instance
    if _llm_engine_instance is None:
        _llm_engine_instance = LLMEngine()
    return _llm_engine_instance
