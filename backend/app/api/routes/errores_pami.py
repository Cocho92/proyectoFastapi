import uuid
from typing import Any
import logging
from fastapi import APIRouter, HTTPException,BackgroundTasks,UploadFile, File
from fastapi.responses import JSONResponse
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message,ExcelProcessResponse
from app.models import ExcelProcessResponse
from app.utiles.regex_patterns import PATRONES_DEFAULT
from app.services.excel_processor import ExcelProcessorService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/errores_pami", tags=["errores_pami"])


@router.post(
    "/procesar/", 
    response_model=ExcelProcessResponse,
    status_code=202,
    summary="Procesar archivo Excel y actualizar Google Sheets",
    description="Sube un archivo Excel, procesa su contenido y actualiza un Google Sheet con los resultados."
)
async def procesar_excel(
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    archivo: UploadFile = File(...),
    spreadsheet_key: str = '1cv-UKJPZcigYuvGW__J2ttoBg2gUkaSfYS2Uvsk6iA8',
    columna_a_procesar: int = 0,
    aplicar_patrones_default: bool = True
):
    """
    Endpoint para subir un archivo Excel, procesarlo y actualizar Google Sheets
    """
    # Verificar que el archivo sea Excel
    if not archivo.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="El archivo debe ser Excel (.xlsx o .xls)")
    
    try:
        # Leer el contenido del archivo directamente en memoria
        contenido = await archivo.read()
        
        # Determinar patrones a usar
        patrones = PATRONES_DEFAULT if aplicar_patrones_default else []
        
        # Procesador de Excel
        excel_processor = ExcelProcessorService()
        
        # Procesar el archivo (en segundo plano)
        background_tasks.add_task(
            excel_processor.procesar_excel_a_gsheets, 
            contenido, 
            spreadsheet_key, 
            patrones, 
            columna_a_procesar
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "mensaje": "Archivo recibido. Procesamiento iniciado en segundo plano.",
                "archivo": archivo.filename,
                "spreadsheet_key": spreadsheet_key,
                "google_sheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_key}"
            }
        )
    
    except Exception as e:
        logger.error(f"Error al procesar la solicitud: {e}")
        raise HTTPException(status_code=500, detail=str(e))