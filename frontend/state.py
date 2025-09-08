# mistral_ai_study_assistant/state.py
import reflex as rx
from .services.llm_service import llm_service

class State(rx.State):
    """Estado compartilhado para a aplicação."""
    
    question: str = ""
    chat_history: list[list[str]] = []
    is_loading: bool = False
    uploaded_file: str = ""

    def set_question(self, question: str):
        """Define a pergunta atual."""
        self.question = question

    def add_to_chat(self, question: str, answer: str):
        """Adiciona uma pergunta e resposta ao histórico."""
        self.chat_history.append([question, answer])

    def clear_chat(self):
        """Limpa o histórico do chat."""
        self.chat_history = []
        self.uploaded_file = ""

    async def handle_upload(self, files: list[rx.UploadFile]):
        """Manipula o upload de arquivos."""
        if files:
            self.uploaded_file = files[0].filename
            # Aqui você adicionaria a lógica de processamento do arquivo
            return rx.window_alert(f"Arquivo {files[0].filename} carregado!")
        return rx.window_alert("Nenhum arquivo selecionado!")

    async def answer_question(self):
        """Responde a pergunta usando o Mistral AI."""
        if not self.question.strip():
            return
            
        self.is_loading = True
        yield  # Atualiza a UI para mostrar loading
        
        try:
            # Simula uma resposta do LLM (substitua pela chamada real ao Mistral)
            answer = f"Resposta para: {self.question}"
            self.add_to_chat(self.question, answer)
            self.question = ""  # Limpa a pergunta após responder
            
        except Exception as e:
            self.add_to_chat(self.question, f"Erro: {str(e)}")
        finally:
            self.is_loading = False