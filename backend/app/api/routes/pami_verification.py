import logging
from typing import Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.api.deps import CurrentUser
from app.models import PAMIVerificationRequest, PAMIVerificationResponse
from app.services.pami_verification_service import PAMIVerificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pami-verification", tags=["pami-verification"])


@router.post("/verify-excel", response_model=PAMIVerificationResponse)
async def verificar_excel_pami(
    current_user: CurrentUser,
    archivo_excel: UploadFile = File(..., description="Archivo Excel con URLs de PAMI"),
    columna_urls: str = Form(default="Id", description="Nombre de la columna que contiene las URLs/IDs"),
    columnas_adicionales: str = Form(
        default="Paciente,Fecha,F. Alta,Observacion,Diagnostico,Motivo",
        description="Columnas adicionales separadas por comas"
    ),
    batch_size: int = Form(default=10, description="Tamaño del bloque de pestañas a procesar"),
    delay_seconds: int = Form(default=1, description="Tiempo de espera en segundos entre bloques")
) -> Any:
    """
    Verifica URLs de PAMI desde un archivo Excel.
    
    Recibe un archivo Excel con URLs/IDs de PAMI, las verifica usando Playwright,
    y devuelve archivos HTML y Excel con los resultados procesados.
    
    Args:
        archivo_excel: Archivo Excel con las URLs a verificar
        columna_urls: Nombre de la columna que contiene las URLs/IDs  
        columnas_adicionales: Lista de columnas adicionales separadas por comas
        batch_size: Cantidad de URLs a procesar en paralelo
        delay_seconds: Tiempo de espera entre lotes de procesamiento
    
    Returns:
        PAMIVerificationResponse con archivos procesados y estadísticas
    """
    
    # Validar archivo
    if not archivo_excel.filename:
        raise HTTPException(status_code=400, detail="No se proporcionó un archivo")
    
    if not archivo_excel.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400, 
            detail="El archivo debe ser un Excel válido (.xlsx o .xls)"
        )
    
    logger.info(f"Usuario {current_user.email} inició verificación PAMI con archivo: {archivo_excel.filename}")
    
    try:
        # Preparar configuración
        columnas_list = [col.strip() for col in columnas_adicionales.split(",") if col.strip()]
        
        request_data = PAMIVerificationRequest(
            columna_urls=columna_urls,
            columnas_adicionales=columnas_list,
            batch_size=batch_size,
            delay_seconds=delay_seconds
        )
        
        # Procesar archivo
        resultado = await PAMIVerificationService.verificar_excel_pami(
            archivo_excel.file, 
            request_data
        )
        
        logger.info(f"Verificación PAMI completada para usuario {current_user.email}")
        logger.info(f"Estadísticas: {resultado.estadisticas.model_dump()}")
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en verificación PAMI: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error interno del servidor durante la verificación"
        )


@router.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint para verificar disponibilidad del servicio"""
    try:
        # Verificar que playwright esté disponible
        import playwright
        
        # Intentar obtener versión de manera segura
        try:
            version = playwright.__version__
        except:
            version = "unknown"
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": "pami-verification",
                "playwright_available": True,
                "playwright_version": version
            }
        )
    except ImportError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy", 
                "service": "pami-verification",
                "playwright_available": False,
                "error": "Playwright no está disponible"
            }
        )


@router.post("/verify-excel-test", include_in_schema=False)
async def verificar_excel_pami_test(
    archivo_excel: UploadFile = File(..., description="Archivo Excel con URLs de PAMI"),
    columna_urls: str = Form(default="Id", description="Nombre de la columna que contiene las URLs/IDs"),
    columnas_adicionales: str = Form(
        default="Paciente,Fecha,F. Alta,Observacion,Diagnostico,Motivo",
        description="Columnas adicionales separadas por comas"
    ),
    batch_size: int = Form(default=2, description="Tamaño del bloque de pestañas a procesar"),
    delay_seconds: int = Form(default=1, description="Tiempo de espera en segundos entre bloques")
) -> Any:
    """
    ENDPOINT DE PRUEBA SIN AUTENTICACIÓN
    ⚠️ SOLO PARA TESTING - REMOVER EN PRODUCCIÓN
    """
    
    # Validar archivo
    if not archivo_excel.filename:
        raise HTTPException(status_code=400, detail="No se proporcionó un archivo")
    
    if not archivo_excel.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400, 
            detail="El archivo debe ser un Excel válido (.xlsx o .xls)"
        )
    
    logger.info(f"TEST: Verificación PAMI iniciada con archivo: {archivo_excel.filename}")
    
    try:
        # Preparar configuración
        columnas_list = [col.strip() for col in columnas_adicionales.split(",") if col.strip()]
        
        request_data = PAMIVerificationRequest(
            columna_urls=columna_urls,
            columnas_adicionales=columnas_list,
            batch_size=batch_size,
            delay_seconds=delay_seconds
        )
        
        # Procesar archivo
        resultado = await PAMIVerificationService.verificar_excel_pami(
            archivo_excel.file, 
            request_data
        )
        
        logger.info(f"TEST: Verificación PAMI completada")
        logger.info(f"TEST: Estadísticas: {resultado.estadisticas.model_dump()}")
        
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TEST: Error inesperado en verificación PAMI: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error interno del servidor durante la verificación"
        )