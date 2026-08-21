# validador_sim.py
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import io

# Importa os módulos do seu projeto
import parser
import schemas
import regras

app = FastAPI(title="Validador SIM API")

# Habilita CORS para permitir que o navegador envie requisições sem bloqueio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/validar")
async def validar_csv(file: UploadFile = File(...)):
    """
    Recebe o CSV enviado pelo frontend, executa o parser e aplica 
    as regras de validação/schemas do projeto.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="O arquivo enviado precisa ser um CSV.")

    try:
        content = await file.read()
        
        # 1. Executa o parser do seu projeto
        # Se seu parser aceitar bytes, passe 'content'; se aceitar string, use 'content.decode("utf-8")'
        raw_data = parser.carregar(content) 

        # 2. Executa a validação usando schemas e regras
        relatorio = regras.validar(raw_data, schema=schemas.SIMSchema)

        # Exemplo de estrutura esperada no retorno JSON:
        # {
        #    "headers": ["coluna1", "coluna2", ...],
        #    "total_rows": 100,
        #    "valid_rows": 85,
        #    "error_rows": 15,
        #    "rows": [
        #        {"id": 1, "status": "valid", "data": [...], "errors": []},
        #        {"id": 2, "status": "error", "data": [...], "errors": ["Campo X é obrigatório"]}
        #    ]
        # }
        return relatorio

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo: {str(e)}")

# Servir a página HTML diretamente no endpoint raiz (opcional)
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run("validador_sim:app", host="127.0.0.1", port=8000, reload=True)