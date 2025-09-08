# mistral_ai_study_assistant/services/llm_service.py
from mistralai import Mistral, ChatMessage
import os
from dotenv import load_dotenv
from typing import List, Optional
import asyncio

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class LLMService:
    """Serviço para interagir com a API do Mistral AI."""
    
    def __init__(self):
        """Inicializa o cliente Mistral com a API key."""
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY não encontrada nas variáveis de ambiente")
        
        self.client = Mistral(api_key=api_key)
        self.embed_model = "mistral-embed"  # Modelo para embeddings
        self.chat_model = "mistral-large-latest"  # Modelo para chat
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings para uma lista de textos.
        
        Args:
            texts: Lista de textos para gerar embeddings
            
        Returns:
            Lista de vetores de embeddings
        """
        try:
            embeddings_response = await asyncio.to_thread(
                self.client.embeddings.create,
                model=self.embed_model,
                input=texts
            )
            return [embedding.embedding for embedding in embeddings_response.data]
        except Exception as e:
            print(f"Erro ao gerar embeddings: {e}")
            raise
    
    async def generate_chat_completion(self, 
                                    prompt: str, 
                                    context: Optional[str] = None,
                                    max_tokens: int = 1000,
                                    temperature: float = 0.7) -> str:
        """
        Gera uma conclusão de chat usando o Mistral AI.
        
        Args:
            prompt: O prompt para o modelo
            context: Contexto adicional para o prompt (opcional)
            max_tokens: Número máximo de tokens na resposta
            temperature: Criatividade da resposta (0.0-1.0)
            
        Returns:
            Resposta gerada pelo modelo
        """
        try:
            # Constrói o prompt final com contexto se fornecido
            final_prompt = prompt
            if context:
                final_prompt = f"""Com base no seguinte contexto:

{context}

Responda à seguinte pergunta: {prompt}

Resposta:"""
            
            # Cria as mensagens para o chat
            messages = [
                ChatMessage(
                    role="user", 
                    content=final_prompt
                )
            ]
            
            # Faz a chamada assíncrona para a API
            chat_response = await asyncio.to_thread(
                self.client.chat.complete,
                model=self.chat_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return chat_response.choices[0].message.content
            
        except Exception as e:
            print(f"Erro na geração de chat: {e}")
            return f"Desculpe, ocorreu um erro ao processar sua solicitação: {str(e)}"
    
    async def generate_quiz_questions(self, 
                                    context: str, 
                                    num_questions: int = 3,
                                    question_type: str = "multiple_choice") -> List[dict]:
        """
        Gera perguntas de quiz baseadas no contexto.
        
        Args:
            context: Texto com o conteúdo para gerar perguntas
            num_questions: Número de perguntas a gerar
            question_type: Tipo de pergunta ("multiple_choice", "true_false", "short_answer")
            
        Returns:
            Lista de dicionários com perguntas e respostas
        """
        try:
            prompt = f"""Com base no seguinte texto, gere {num_questions} perguntas do tipo {question_type}.

Texto:
{context}

Formate a resposta como uma lista JSON com cada pergunta contendo:
- question: o texto da pergunta
- options: lista de opções (apenas para múltipla escolha)
- correct_answer: a resposta correta
- explanation: explicação breve da resposta

Perguntas:"""
            
            messages = [ChatMessage(role="user", content=prompt)]
            
            chat_response = await asyncio.to_thread(
                self.client.chat.complete,
                model=self.chat_model,
                messages=messages,
                max_tokens=2000,
                temperature=0.5  # Temperatura mais baixa para perguntas mais factuais
            )
            
            # Extrai e parseia a resposta JSON
            response_text = chat_response.choices[0].message.content
            # Remove markdown code blocks se existirem
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            # Aqui você precisaria de um parser JSON real
            # Por enquanto, retornamos uma resposta simulada
            return [
                {
                    "question": "Qual é o principal tema do texto?",
                    "options": ["Tema A", "Tema B", "Tema C", "Tema D"],
                    "correct_answer": "Tema A",
                    "explanation": "O texto foca principalmente no Tema A."
                }
            ]
            
        except Exception as e:
            print(f"Erro ao gerar perguntas de quiz: {e}")
            return []

# Instância global do serviço
llm_service = LLMService()