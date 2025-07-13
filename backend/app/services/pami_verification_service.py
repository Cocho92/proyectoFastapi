import io
import logging
import pandas as pd
import time
import json
import base64
import asyncio
from datetime import datetime
from typing import Any, BinaryIO
from playwright.async_api import async_playwright
from fastapi import HTTPException

from app.core.config import settings
from app.models import PAMIVerificationRequest, PAMIVerificationResponse, PAMIVerificationStats, PAMIURLData

logger = logging.getLogger(__name__)


class PAMIVerificationService:
    """Servicio para verificar URLs de PAMI usando Playwright"""

    @staticmethod
    async def verificar_excel_pami(
        archivo_excel: BinaryIO,
        request_data: PAMIVerificationRequest
    ) -> PAMIVerificationResponse:
        """
        Procesa un archivo Excel con URLs de PAMI y genera archivos HTML y Excel de resultados
        
        Args:
            archivo_excel: Archivo Excel en memoria
            request_data: Configuración de la verificación
        
        Returns:
            PAMIVerificationResponse con archivos codificados y estadísticas
        """
        try:
            # Leer datos del Excel
            df_datos = await PAMIVerificationService._obtener_datos_excel(
                archivo_excel, request_data.columna_urls, request_data.columnas_adicionales
            )
            
            if df_datos.empty:
                raise HTTPException(status_code=400, detail="No se encontraron datos válidos en el archivo Excel")
            
            # Verificar URLs con Playwright
            resultados = await PAMIVerificationService._verificar_urls_playwright(
                df_datos, request_data
            )
            
            # Generar archivos
            archivo_excel_b64, nombre_excel = await PAMIVerificationService._generar_excel_resultados(
                resultados["df_resultados"], 
                resultados["urls_coincidentes"], 
                resultados["urls_no_coincidentes"]
            )
            
            archivo_html_b64, nombre_html = await PAMIVerificationService._generar_html_resultados(
                resultados["urls_para_html"]
            )
            
            # Calcular estadísticas
            stats = PAMIVerificationStats(
                total_urls=len(df_datos),
                urls_coincidentes=len(resultados["urls_coincidentes"]),
                urls_no_coincidentes=len(resultados["urls_no_coincidentes"]),
                urls_con_error=resultados["urls_con_error"]
            )
            
            return PAMIVerificationResponse(
                mensaje=f"Verificación completada. {stats.urls_coincidentes} URLs coincidentes de {stats.total_urls} total.",
                estadisticas=stats,
                archivo_excel_base64=archivo_excel_b64,
                archivo_html_base64=archivo_html_b64,
                nombre_archivo_excel=nombre_excel,
                nombre_archivo_html=nombre_html
            )
            
        except Exception as e:
            logger.error(f"Error en verificación PAMI: {e}")
            raise HTTPException(status_code=500, detail=f"Error al procesar verificación: {str(e)}")

    @staticmethod
    async def _obtener_datos_excel(archivo: BinaryIO, columna_urls: str, columnas_adicionales: list[str]) -> pd.DataFrame:
        """Lee y valida datos del archivo Excel"""
        try:
            # Leer archivo Excel
            contenido = archivo.read()
            archivo.seek(0)  # Reset para posible re-lectura
            df = pd.read_excel(io.BytesIO(contenido))
            
            # Verificar columnas requeridas
            columnas_requeridas = [columna_urls] + columnas_adicionales
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                logger.error(f"Columnas faltantes: {columnas_faltantes}")
                logger.info(f"Columnas disponibles: {list(df.columns)}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Columnas faltantes en el archivo: {columnas_faltantes}"
                )
            
            # Filtrar filas válidas
            df_filtrado = df[df[columna_urls].notna()].copy()
            df_resultado = df_filtrado[columnas_requeridas].copy()
            
            logger.info(f"Se cargaron {len(df_resultado)} registros del archivo Excel")
            return df_resultado
            
        except Exception as e:
            logger.error(f"Error al leer archivo Excel: {e}")
            raise HTTPException(status_code=400, detail=f"Error al procesar archivo Excel: {str(e)}")

    @staticmethod
    async def _verificar_urls_playwright(df_datos: pd.DataFrame, request_data: PAMIVerificationRequest) -> dict[str, Any]:
        """Verifica URLs usando Playwright"""
        
        # Estructuras para resultados
        columnas_resultado = list(df_datos.columns) + ['URL_Completa', 'Coincide']
        df_resultados = pd.DataFrame(columns=columnas_resultado)
        urls_coincidentes = []
        urls_no_coincidentes = []
        urls_para_html = []
        urls_con_error = 0
        
        logger.info(f"Iniciando verificación de {len(df_datos)} URLs")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=settings.PAMI_HEADLESS)
                context = await browser.new_context()
                
                primera_pagina = None
                login_realizado = False
                
                # Procesar en lotes
                for i in range(0, len(df_datos), request_data.batch_size):
                    batch_df = df_datos.iloc[i:i + request_data.batch_size]
                    logger.info(f"Procesando lote {i//request_data.batch_size + 1}")
                    
                    for idx, row in batch_df.iterrows():
                        url_id = str(row[request_data.columna_urls])
                        url_completa = f"{settings.PAMI_BASE_URL}{url_id}"
                        
                        try:
                            page = await context.new_page()
                            logger.info(f"Verificando URL: {url_id}")
                            await page.goto(url_completa)
                            
                            # Manejo de login
                            if await page.locator(settings.PAMI_LOGIN_FORM_SELECTOR).is_visible():
                                if not login_realizado:
                                    await PAMIVerificationService._iniciar_sesion(page)
                                    login_realizado = True
                                    primera_pagina = page
                                else:
                                    await page.close()
                                    await primera_pagina.goto(url_completa)
                                    page = primera_pagina
                            
                            # Esperar carga
                            await page.wait_for_load_state('domcontentloaded')
                            await page.wait_for_timeout(1000)  # 1 segundo adicional
                            
                            # Verificar contenido
                            content = await page.content()
                            coincide = settings.PAMI_SEARCH_TEXT in content
                            
                            # Debug: logging detallado
                            logger.info(f"URL {url_id}: Contenido cargado - {len(content)} caracteres")
                            logger.info(f"URL {url_id}: Buscando texto '{settings.PAMI_SEARCH_TEXT}'")
                            logger.info(f"URL {url_id}: Título de página: {await page.title()}")
                            
                            # Log parcial del contenido para diagnóstico
                            if len(content) < 500:
                                logger.info(f"URL {url_id}: Contenido completo: {content[:500]}")
                            else:
                                logger.info(f"URL {url_id}: Primeros 500 chars: {content[:500]}")
                                logger.info(f"URL {url_id}: Últimos 500 chars: {content[-500:]}")
                            
                            logger.info(f"URL {url_id}: Coincide = {coincide}")
                            
                            # Procesar resultado
                            df_resultados = PAMIVerificationService._procesar_resultado_url(
                                row, url_id, url_completa, coincide, request_data.columna_urls,
                                df_resultados, urls_coincidentes, urls_no_coincidentes, urls_para_html
                            )
                            
                            if page != primera_pagina:
                                await page.close()
                                
                        except Exception as e:
                            logger.error(f"Error al procesar {url_id}: {e}")
                            urls_con_error += 1
                            
                            # Agregar como error
                            df_resultados = PAMIVerificationService._procesar_resultado_url(
                                row, url_id, url_completa, False, request_data.columna_urls,
                                df_resultados, urls_coincidentes, urls_no_coincidentes, urls_para_html
                            )
                            
                            try:
                                if page != primera_pagina:
                                    await page.close()
                            except:
                                pass
                    
                    # Esperar entre lotes
                    await asyncio.sleep(request_data.delay_seconds)
                
                await browser.close()
                
        except Exception as e:
            logger.error(f"Error en Playwright: {e}")
            raise
        
        return {
            "df_resultados": df_resultados,
            "urls_coincidentes": urls_coincidentes,
            "urls_no_coincidentes": urls_no_coincidentes,
            "urls_para_html": urls_para_html,
            "urls_con_error": urls_con_error
        }

    @staticmethod
    async def _iniciar_sesion(page):
        """Inicia sesión en PAMI"""
        try:
            logger.info("Iniciando sesión en PAMI...")
            await page.fill('input[name="UserName"]', settings.PAMI_LOGIN_USER)
            await page.fill('input[name="Password"]', settings.PAMI_LOGIN_PASSWORD)
            await page.wait_for_selector('select#ubicCodigo', timeout=10000)
            
            await page.select_option('select#depoCodigo', value=str(settings.PAMI_DEPOT_CODE))
            await page.select_option('select#ubicCodigo', value=str(settings.PAMI_LOCATION_CODE))
            
            await page.click('input[type="submit"]')
            await page.wait_for_load_state('networkidle')
            logger.info("Sesión iniciada correctamente")
        except Exception as e:
            logger.error(f"Error al iniciar sesión: {e}")
            raise

    @staticmethod
    def _procesar_resultado_url(
        row, url_id: str, url_completa: str, coincide: bool, columna_urls: str,
        df_resultados: pd.DataFrame, urls_coincidentes: list, urls_no_coincidentes: list, urls_para_html: list
    ) -> pd.DataFrame:
        """Procesa el resultado de una URL verificada"""
        
        # Crear nueva fila para resultados
        nueva_fila = row.copy()
        nueva_fila['URL_Completa'] = url_completa
        nueva_fila['Coincide'] = coincide
        
        df_nueva_fila = pd.DataFrame([nueva_fila])
        df_resultados = pd.concat([df_resultados, df_nueva_fila], ignore_index=True)
        
        # Clasificar resultado
        if coincide:
            logger.info(f"✓ Texto encontrado en: {url_id}")
            urls_coincidentes.append(row.to_dict())
            
            # Agregar a HTML
            urls_para_html.append({
                'name': f"Paciente: {row.get('Paciente', 'N/A')} - ID: {url_id}",
                'url': url_completa,
                'id': f"url_{url_id}",
                'paciente': str(row.get('Paciente', 'N/A')),
                'fecha': str(row.get('Fecha', 'N/A')),
                'f_alta': str(row.get('F. Alta', 'N/A')),
                'observacion': str(row.get('Observacion', 'N/A')),
                'diagnostico': str(row.get('Diagnostico', 'N/A')),
                'motivo': str(row.get('Motivo', 'N/A')),
            })
        else:
            logger.info(f"✗ Texto NO encontrado en: {url_id}")
            urls_no_coincidentes.append(row.to_dict())
        
        return df_resultados

    @staticmethod
    async def _generar_excel_resultados(df_resultados: pd.DataFrame, urls_coincidentes: list, urls_no_coincidentes: list) -> tuple[str, str]:
        """Genera archivo Excel con resultados"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f'URLs_Resultados_PAMI_{timestamp}.xlsx'
            
            # Crear archivo en memoria
            excel_buffer = io.BytesIO()
            
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                # Hoja con todos los resultados
                df_resultados.to_excel(writer, sheet_name='Todos_Resultados', index=False)
                
                # Hojas separadas
                if urls_coincidentes:
                    df_coincidentes = pd.DataFrame(urls_coincidentes)
                    df_coincidentes.to_excel(writer, sheet_name='Coincidentes', index=False)
                
                if urls_no_coincidentes:
                    df_no_coincidentes = pd.DataFrame(urls_no_coincidentes)
                    df_no_coincidentes.to_excel(writer, sheet_name='No_Coincidentes', index=False)
            
            # Codificar en base64
            excel_buffer.seek(0)
            excel_b64 = base64.b64encode(excel_buffer.getvalue()).decode('utf-8')
            
            logger.info(f"Archivo Excel generado: {nombre_archivo}")
            return excel_b64, nombre_archivo
            
        except Exception as e:
            logger.error(f"Error al generar Excel: {e}")
            raise

    @staticmethod
    async def _generar_html_resultados(urls_para_html: list) -> tuple[str, str]:
        """Genera archivo HTML interactivo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f'ControlUrls_PAMI_{timestamp}.html'
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            # Plantilla HTML (simplificada para la integración)
            html_template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control de OPs Internaciones PAMI</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 30px; }}
        h1 {{ color: #2c3e50; text-align: center; }}
        .container {{ background-color: #f9f9f9; border-radius: 8px; padding: 25px; }}
        .stats {{ background-color: #e3f2fd; border-radius: 5px; padding: 10px 15px; margin-bottom: 20px; }}
        .link-item {{ margin: 15px 0; padding: 15px; border: 1px solid #e0e0e0; border-radius: 5px; background-color: #fff; }}
        .patient-info {{ background-color: #e8f4fd; padding: 8px 12px; border-radius: 4px; margin: 8px 0; }}
        a {{ color: #3498db; text-decoration: none; font-weight: bold; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Control de OPs PAMI</h1>
        <div class="stats">
            URLs verificadas: {total_urls} | Fecha de verificación: {fecha}
        </div>
        <div class="links-section">
            <h3>Enlaces verificados:</h3>
            <div id="linksList">
"""

            # Agregar enlaces
            for site in urls_para_html:
                html_template += f"""
                <div class="link-item">
                    <div>
                        <a href="{site['url']}" target="_blank">{site['paciente']}</a>
                    </div>
                    <div class="patient-info">
                        <div><strong>Paciente:</strong> {site['paciente']}</div>
                        <div><strong>Fecha:</strong> {site['fecha']} | <strong>F. Alta:</strong> {site['f_alta']}</div>
                        <div><strong>Motivo:</strong> {site['motivo']}</div>
                        <div><strong>Observación:</strong> {site['observacion']}</div>
                        <div><strong>Diagnóstico:</strong> {site['diagnostico']}</div>
                    </div>
                    <div style="color: #777; font-size: 0.8em; margin-top: 5px;">{site['url']}</div>
                </div>
"""

            html_template += """
            </div>
        </div>
    </div>
</body>
</html>
"""
            
            # Reemplazar valores
            html_content = html_template.format(
                total_urls=len(urls_para_html),
                fecha=fecha_actual
            )
            
            # Codificar en base64
            html_b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
            
            logger.info(f"Archivo HTML generado: {nombre_archivo}")
            return html_b64, nombre_archivo
            
        except Exception as e:
            logger.error(f"Error al generar HTML: {e}")
            raise