import io
import logging
import pandas as pd
import re
import gspread
from fastapi import HTTPException
from app.services.gsheet_service import GoogleSheetsService
from app.utiles.regex_patterns import PATRONES_DEFAULT

logger = logging.getLogger(__name__)

class ExcelProcessorService:
    """Servicio para procesar archivos Excel y actualizar Google Sheets"""
    
    @staticmethod
    async def procesar_excel_a_gsheets(
        contenido_archivo, 
        spreadsheet_key, 
        patrones=None, 
        columna_a_procesar=0
    ):
        """
        Procesa contenido de Excel en memoria y actualiza un Google Sheet con los resultados filtrados
        
        Args:
            contenido_archivo: Bytes del archivo Excel
            spreadsheet_key: ID del Google Sheet donde guardar los resultados
            patrones: Lista de patrones regex para filtrar (usa PATRONES_DEFAULT si es None)
            columna_a_procesar: Índice de la columna a procesar (0 es la primera)
        
        Returns:
            dict: Estadísticas sobre el procesamiento
        """
        if patrones is None:
            patrones = PATRONES_DEFAULT
            
        try:
            # Leer el archivo Excel directamente desde memoria
            df = pd.read_excel(io.BytesIO(contenido_archivo), skiprows=1)
            
            # Rellenar celdas vacías en la columna B (índice 1)
            df.iloc[:, 1] = df.iloc[:, 1].ffill()  # Forward fill para rellenar NaN con el valor anterior
            
            # Seleccionar solo la columna especificada para aplicar los patrones
            columna_seleccionada = df.iloc[:, columna_a_procesar]
            
            # Filtrar las filas que cumplen con al menos uno de los patrones
            cumple_patron = columna_seleccionada.apply(
                lambda valor: any(re.search(patron, str(valor)) for patron in patrones)
            )
            df_no_cumple = df[~cumple_patron].copy()  # Usar copy() para evitar warnings
            df_cumple = df[cumple_patron].copy()  # Usar copy() para evitar warnings
            
            # Agregar columna de conteo a ambos DataFrames
            for df_filtrado in [df_no_cumple, df_cumple]:
                # Obtener columna de IDs (columna 3, índice 2)
                columna_ids = df_filtrado.iloc[:, 2]
                # Calcular conteos específicos para cada DataFrame
                conteo_ids = columna_ids.map(columna_ids.value_counts())
                # Insertar columna en posición 3 (4ta columna)
                df_filtrado.insert(3, "Registros por Afiliado", conteo_ids)
            
            # Autenticación con Google Sheets
            gsheet_service = GoogleSheetsService()
            client = gsheet_service.obtener_cliente_gspread()
            
            # Abrir el spreadsheet por su key
            spreadsheet = client.open_by_key(spreadsheet_key)
            
            # Actualizar las hojas en Google Sheets
            for nombre_hoja, dataframe in [('Criticas', df_no_cumple), ('A revisar', df_cumple)]:
                try:
                    # Si la hoja ya existe, la seleccionamos o creamos una nueva
                    try:
                        worksheet = spreadsheet.worksheet(nombre_hoja)
                    except gspread.exceptions.WorksheetNotFound:
                        worksheet = spreadsheet.add_worksheet(
                            title=nombre_hoja, 
                            rows=dataframe.shape[0]+1, 
                            cols=dataframe.shape[1]
                        )
                    
                    # Actualizar la hoja
                    gsheet_service.df_to_sheet(dataframe, worksheet)
                    
                except Exception as e:
                    logger.error(f"Error al procesar la hoja {nombre_hoja}: {e}")
                    raise
            
            # Aplicar formato al final
            gsheet_service.aplicar_formato_hojas(spreadsheet)
            return {
                "registros_totales": len(df),
                "registros_criticos": len(df_no_cumple),
                "registros_a_revisar": len(df_cumple),
                "spreadsheet_title": spreadsheet.title,
                "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_key}"
            }
        
        except Exception as e:
            logger.error(f"Error en el procesamiento del Excel: {e}")
            raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")
        