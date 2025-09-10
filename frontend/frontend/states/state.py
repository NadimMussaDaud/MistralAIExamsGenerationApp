import reflex as rx
import pdfplumber
import os
from typing import TypedDict
import mistralai
import logging
from dotenv import load_dotenv
load_dotenv()

client = mistralai.Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
model = "mistral-large-latest"

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ChatMessage(TypedDict):
    role: str
    content: str


class State(rx.State):
    chat_history: list[ChatMessage] = [
        {
            "role": "assistant",
            "content": "Hello! I'm a PDF assistant. Upload a PDF and I'll help you with any questions you have about it.",
        }
    ]
    current_question: str = ""
    processing: bool = False
    is_uploading: bool = False
    uploaded_pdf: str = ""
    pdf_text: str = ""

    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            yield rx.toast.warning("No file selected. Please choose a PDF to upload.")
            return
        self.is_uploading = True
        yield
        try:
            file = files[0]
            
            file_path = os.path.join(UPLOAD_DIR, file.name)
            # Save the uploaded file to disk
            with open(file_path, "wb") as f:
                f.write(await file.read())
            self.uploaded_pdf = file.name

            # Optionally, extract text from PDF for later use
            try:
                with pdfplumber.open(file_path) as pdf:
                    self.pdf_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            except Exception as e:
                logging.warning(f"Could not extract text from PDF: {e}")
                self.pdf_text = ""

            self.chat_history.append(
                {
                    "role": "assistant",
                    "content": f"Successfully uploaded {self.uploaded_pdf}. What would you like to know about it?",
                }
            )
            yield rx.toast.success(f"Uploaded {file.name}")
        except Exception as e:
            logging.exception(f"Upload failed: {e}")
            yield rx.toast.error("Upload failed. Please try again.")
        finally:
            self.is_uploading = False

    @rx.event(background=True)
    async def process_question(self):
        async with self:
            self.chat_history.append({"role": "user", "content": self.current_question})
            self.processing = True
            self.current_question = ""
        try:
            if not self.pdf_text:
                response_content = "Please upload a PDF first."
            else:
                completion = await client.chat.complete_async(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a helpful assistant. Use the following PDF content to answer the user's question and only use the pdf for it and If asked about anything outside dont answer with anything outside the PDF's scope. Content: {self.pdf_text}",
                        },
                        {"role": "user", "content": self.chat_history[-1]["content"]},
                    ],
                )
                response_content = completion.choices[0].message.content
            async with self:
                self.chat_history.append(
                    {"role": "assistant", "content": response_content}
                )
        except Exception as e:
            logging.exception(f"Error processing question: {e}")
            async with self:
                self.chat_history.append(
                    {"role": "assistant", "content": f"An error occurred: {str(e)}"}
                )
        finally:
            async with self:
                self.processing = False

    @rx.event
    def answer(self, form_data: dict):
        question = form_data.get("question", "").strip()
        if not question or self.processing:
            return
        self.current_question = question
        return State.process_question