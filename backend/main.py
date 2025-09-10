import uvicorn
from app.api.endpoints import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
     allow_origins=[
        "http://localhost:3000",    # React dev server
        "http://127.0.0.1:3000",    # React alternative
        "https://*.github.dev",     # GitHub Codespaces
        "https://*.githubpreview.dev", # GitHub Preview
        "https://*.app.github.dev"  # GitHub Codespaces
    ],  # Ou especifique seu domínio para mais segurança
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI backend!"}

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
