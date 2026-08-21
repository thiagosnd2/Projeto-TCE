from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import parser, schemas, regras  # Módulos do seu projeto[cite: 1]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/validar")
async def validar_csv(file: UploadFile = File(...)):
    conteudo = await file.read()
    dados_parseados = parser.carregar(conteudo)
    erros, estatisticas = regras.validar(dados_parseados, schema=schemas.SIMSchema)
    
    return {
        "estatisticas": estatisticas,
        "resultados": erros
    }