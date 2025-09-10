from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
import os
import pymupdf as fitz
from mistralai import Mistral
import asyncio
import logging
import reflex as rx
from frontend.states.state import ChatMessage
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

api = FastAPI()
api.add_middleware(
    CORSMiddleware,
     allow_origins=[ "*" ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "mistral-large-latest"

mistral_api_key = os.getenv("MISTRAL_API_KEY")
if not mistral_api_key:
    logging.warning(
        "MISTRAL_API_KEY environment variable not set. Exam generation will not work."
    )
    mistral_client = None
else:
    mistral_client = Mistral(api_key=mistral_api_key)

async def exam_generator(pdf_texts: list[str]):
    """Generator function to stream the exam from MistralAI."""
    if not mistral_client:
        yield "Error: MistralAI client is not configured on the server."
        return
    prompt_parts = [
        "You are an expert in creating educational materials. Your task is to generate a multiple-choice exam based on the provided PDF documents.",
        "The first document is an example of a previous exam, which you should use to understand the desired format, style, and difficulty.",
        "The subsequent documents are lecture slides or notes containing the source material for the new questions.",
        "Create new, original questions based on the source material that mimic the style of the example exam.",
        "Here is the content from the documents:",
    ]
    for i, text in enumerate(pdf_texts):
        doc_type = "Example Exam" if i == 0 else "Lecture Slides/Notes"
        prompt_parts.append(f"\n--- Document {i + 1} ({doc_type}) ---\n{text}\n")
    prompt_parts.append(
        "\n--- End of Documents ---\n\nPlease generate the new multiple-choice exam now."
    )
    full_prompt = "\n".join(prompt_parts)
    messages = [ChatMessage(role="user", content=full_prompt)]
    try:
        for chunk in mistral_client.chat_stream(model=MODEL_NAME, messages=messages):
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
                await asyncio.sleep(0.01)
    except Exception as e:
        error_message = f"An error occurred while communicating with MistralAI: {e}"
        logging.exception(error_message)
        yield error_message



@api.post("/generate-exam")
async def generate_exam_endpoint(files: list[UploadFile] = File(...)):
    pdf_texts = []
    for file in files:
        try:
            file_bytes = await file.read()
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                text = "".join((page.get_text() for page in doc))
                pdf_texts.append(text)
        except Exception as e:
            logging.exception(f"Failed to process PDF file: {file.filename}")
            pass
    return StreamingResponse(exam_generator(pdf_texts), media_type="text/plain")

__all__ = ["generate_exam_endpoint"]