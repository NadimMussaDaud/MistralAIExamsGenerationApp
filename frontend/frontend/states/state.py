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
system_prompt = """
You are an expert exam writer for a university course. Your task is to generate new exam questions based on provided course material and the style of previous exams.

**Style Guidelines to Follow from Previous Exams:**
*   **Tone:** {describe the tone, e.g., formal, precise, challenging}
*   **Structure:** {describe the structure, e.g., "Section A: Multiple Choice, Section B: Short Answer, Section C: Essay"}
*   **Question Phrasing:** {describe how questions are phrased, e.g., "Questions often start with 'Compare and contrast...', 'Explain the significance of...'"}
*   **Difficulty Level:** {describe the difficulty, e.g., "Focus on application, not just memorization."}
*   **Specific Instructions:** {include any specific instructions from the old exams, e.g., "Show all your work for full credit."}

**Your Process:**
1.  Analyze the provided course slides to understand the key topics and concepts.
2.  Analyze the previous exams to understand the exact style, structure, and difficulty you must replicate.
3.  Generate a new exam that comprehensively tests the material from the slides in the exact style of the previous exams.
4.  **Most Importantly: DO NOT invent topics not covered in the provided slides.**
"""
'''
user_prompt = f"""
**COURSE SLIDES CONTENT:**
{slides_text}

**PREVIOUS EXAMS FOR STYLE REFERENCE:**
{previous_exams_text}

**TASK:**
Based on the course slides above, and meticulously mimicking the style, structure, and difficulty of the previous exams provided, generate a complete new exam. The exam should cover the major topics from the slides.
"""

'''
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
    slides_text: list[str] = []
    exams_text: list[str] = []

    async def classify_document(self, text : str) -> str:
        """Uses the Mistral API to classify a document as 'slide' or 'test'."""

        prompt = f"""
        You are an expert document classifier. Your only task is to analyze the content from the file provided below and classify it into one of two categories:

        - **"slide"**: The content is structured like lecture slides or presentation material. It is typically concise, contains bullet points, headings, diagrams, and summaries of topics.
        - **"test"**: The content is an exam, quiz, or assessment. It contains questions (e.g., multiple choice, short answer, essay), instructions for test-takers, point values, and answer fields.

        **CONTENT TO ANALYZE:**
        ```
        {text[:8000]} # Send the first ~8000 characters for cost efficiency
        ```

        **IMPORTANT:** Respond ONLY with the single, lowercase word "slide" or "test". Do not write any other text, explanations, or apologies.
        """

        response = await client.chat.complete_async(
            model="mistral-small-latest", # Perfectly sufficient for this task
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0 # Deterministic output
        )

        classification = response.choices[0].message.content.strip().lower()
        return classification if classification in ["slide", "test"] else "unknown"

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
            if file.name.lower().endswith(".pdf"):
                try:
                    with pdfplumber.open(file_path) as pdf:
                        self.pdf_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                        classification = await self.classify_document(self.pdf_text[:8000])
                        if classification == "slide":
                            self.slides_text.append(self.pdf_text)
                            print("Classified as slide")
                        elif classification == "test":
                            self.exams_text.append(self.pdf_text)
                            print("Classified as test")

                except Exception as e:
                    logging.warning(f"Could not extract text from PDF: {e}")
                    self.pdf_text = ""
            elif file.name.lower().endswith(".txt"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        self.pdf_text = f.read()
                        classification = await self.classify_document(self.pdf_text[:8000])
                        if classification == "slide":
                            self.slides_text.append(self.pdf_text)
                            print("Classified as slide (txt)")
                        elif classification == "test":
                            self.exams_text.append(self.pdf_text)
                            print("Classified as test (txt)")
                except Exception as e:
                    logging.warning(f"Could not extract text from TXT: {e}")
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
                    temperature=0.2,
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

    @rx.event(background=True)
    async def generate_exam(self):
        async with self:
            self.processing = True
        try:
            if not self.slides_text or not self.exams_text:
                response_content = "Please upload both slides and previous exams before generating a new exam."
            else:
                completion = await client.chat.complete_async(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"""
**COURSE SLIDES CONTENT:**
{self.slides_text}

**PREVIOUS EXAMS FOR STYLE REFERENCE:**
{self.exams_text}

**TASK:**
Based on the course slides above, and meticulously mimicking the style, structure, and difficulty of the previous exams provided, generate a complete new exam. The exam should cover the major topics from the slides.
"""}
                    ],
                    temperature=0.3,
                )
                response_content = completion.choices[0].message.content
            async with self:
                self.chat_history.append(
                    {"role": "assistant", "content": response_content}
                )
        except Exception as e:
            logging.exception(f"Error generating exam: {e}")
            async with self:
                self.chat_history.append(
                    {"role": "assistant", "content": f"An error occurred: {str(e)}"}
                )
        finally:
            async with self:
                self.processing = False

