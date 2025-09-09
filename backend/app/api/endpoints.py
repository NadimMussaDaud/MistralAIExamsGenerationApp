
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from mistralai import Mistral
import os

router = APIRouter()

# Configure sua chave de API da Mistral


MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "SUA_CHAVE_AQUI")
client = Mistral(api_key=MISTRAL_API_KEY)

@router.post("/generate-questions")
async def generate_questions(
	tests: UploadFile = File(...),
	slides: UploadFile = File(...),
	prompt: str = Form(None)
):
	"""
	Recebe arquivos de testes e slides, retorna novas perguntas geradas pela Mistral.
	"""
	tests_content = await tests.read()
	slides_content = await slides.read()

	# Monta o prompt para a Mistral
	mistral_prompt = (
		prompt or
		f"Gere novas perguntas baseadas nos seguintes testes e slides.\n\nTestes:\n{tests_content.decode()}\n\nSlides:\n{slides_content.decode()}"
	)

	# Chama o modelo da Mistral
	response = client.chat(
		model="mistral-tiny",  # ou outro modelo disponível
		messages=[{"role": "user", "content": mistral_prompt}]
	)

	questions = response.choices[0].message["content"] if response.choices else "Erro ao gerar perguntas."
	return JSONResponse(content={"questions": questions})

@router.post("/upload-documents")
async def upload_documents(files: list[UploadFile] = File(...)):
    saved_files = []
    for file in files:
        content = await file.read()
        # Salve o arquivo no disco ou processe conforme necessário
        with open(f"/tmp/{file.filename}", "wb") as f:
            f.write(content)
        saved_files.append(file.filename)
    return JSONResponse(content={"uploaded_files": saved_files})