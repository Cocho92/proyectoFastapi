import logging
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from app.core.config import settings

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    """Servicio para interactuar con Google Sheets"""
    
    @staticmethod
    def obtener_cliente_gspread():
        """
        Crea y devuelve un cliente autenticado de gspread
        
        Returns:
            Un cliente autenticado de gspread
        """
        scope = ['https://spreadsheets.google.com/feeds', 
                'https://www.googleapis.com/auth/drive']
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                settings.GOOGLE_SHEETS_CREDENTIALS_FILE, scope
            )
            client = gspread.authorize(creds)
            return client
        except Exception as e:
            logger.error(f"Error en la autenticación con Google Sheets: {e}")
            raise
    
    @staticmethod
    def df_to_sheet(df, worksheet):
        """
        Convierte un DataFrame a formato de Google Sheets y actualiza la hoja
        
        Args:
            df: DataFrame a convertir
            worksheet: Worksheet de Google Sheets a actualizar
        """
        try:
            # Limpiar el DataFrame
            df_clean = df.copy()
            
            # Reemplazar NaN/NaT/Inf con cadenas vacías o valores manejables
            df_clean = df_clean.fillna("")  # NaN/NaT → ""
            df_clean = df_clean.replace([float('inf'), float('-inf')], "")  # Inf → ""
            
            # Convertir columnas de fecha a strings
            for col in df_clean.select_dtypes(include=['datetime']).columns:
                df_clean[col] = df_clean[col].astype(str)
            
            # Convertir a lista de listas
            header = df_clean.columns.tolist()
            values = [header] + df_clean.values.tolist()
            
            # Actualizar la hoja
            worksheet.clear()
            worksheet.update(values)
            
        except Exception as e:
            logger.error(f"Error al actualizar la hoja {worksheet.title}: {e}")
            raise

    @staticmethod
    def _obtener_letra_columna(indice):
        """
        Convierte un índice numérico a letra de columna de Excel
        1 -> A, 2 -> B, ... 26 -> Z, 27 -> AA, etc.
        
        Args:
            indice: Índice numérico de columna (empezando en 1)
        
        Returns:
            String con la letra de columna correspondiente
        """
        resultado = ""
        while indice > 0:
            indice, residuo = divmod(indice - 1, 26)
            resultado = chr(65 + residuo) + resultado
        return resultado

    @staticmethod
    def aplicar_formato(worksheet, formato_personalizado=None, ajustar_columnas=True, limite_columnas=None):
        """
        Aplica formato a una hoja de cálculo específica
        
        Args:
            worksheet: Objeto worksheet de gspread
            formato_personalizado: Diccionario con formato personalizado para aplicar
            ajustar_columnas: Si es True, ajusta automáticamente el ancho de las columnas con datos
            limite_columnas: Número máximo de columnas a formatear. Si es None, no hay límite.
        """
        try:
            # Obtener número de filas y columnas
            valores = worksheet.get_all_values()
            num_rows = len(valores)
            
            if num_rows <= 0:  # Hoja vacía
                logger.info(f"La hoja {worksheet.title} está vacía")
                return
                
            # Determinar el número real de columnas con datos
            num_columnas = max(len(fila) for fila in valores) if valores else 0
            
            # Si hay un límite de columnas, aplicarlo
            if limite_columnas and num_columnas > limite_columnas:
                logger.warning(f"La hoja tiene {num_columnas} columnas, formateando solo hasta la columna {limite_columnas}")
                num_columnas = limite_columnas
            
            # Formato por defecto
            formato_default = {
                "horizontalAlignment": "CENTER",
                "verticalAlignment": "MIDDLE",
                "wrapStrategy": "WRAP",
                "backgroundColor": {
                    "red": 1.0,
                    "green": 1.0,
                    "blue": 1.0
                },
                "textFormat": {
                    "foregroundColor": {
                        "red": 0.0,
                        "green": 0.0,
                        "blue": 0.0
                    },
                    "bold": False,
                    "italic": False
                }
            }
            
            # Usar formato personalizado si se proporciona
            formato_final = formato_personalizado if formato_personalizado else formato_default
            
            # Calcular el rango de celdas a formatear basado en datos reales
            ultima_columna = GoogleSheetsService._obtener_letra_columna(num_columnas)
            
            # Aplicar formato a todas las celdas con datos
            rango_formato = f'A1:{ultima_columna}{num_rows}'
            worksheet.format(rango_formato, formato_final)
            
            # Pintar columna C de amarillo
            rango_columna_c = f'C1:C{num_rows}'
            formato_columna_c = {
                "backgroundColor": {"red": 1.0, "green": 1.0, "blue": 0.0}  # Amarillo
            }
            worksheet.format(rango_columna_c, formato_columna_c)

            # Ajustar el ancho de todas las columnas con datos
            if ajustar_columnas and num_columnas > 0:
                for i in range(1, num_columnas + 1):
                    # Truco para forzar actualización del ancho de columna
                    cell_value = worksheet.cell(1, i).value if num_rows >= 1 else ""
                    worksheet.update_cell(1, i, cell_value)
                
            logger.info(f"Formato aplicado correctamente a la hoja {worksheet.title} en el rango {rango_formato}")
        except Exception as e:
            logger.error(f"Error al aplicar formato a {worksheet.title}: {e}")
            raise

    @staticmethod
    def aplicar_formato_hojas(spreadsheet, nombres_hojas=None, formato_personalizado=None, ajustar_columnas=True, limite_columnas=None):
        """
        Aplica formato a múltiples hojas de cálculo
        
        Args:
            spreadsheet: Objeto spreadsheet de gspread
            nombres_hojas: Lista de nombres de hojas a formatear. Si es None, formatea todas las hojas
            formato_personalizado: Diccionario con formato personalizado para aplicar
            ajustar_columnas: Si es True, ajusta automáticamente el ancho de las columnas con datos
            limite_columnas: Número máximo de columnas a formatear. Si es None, no hay límite.
        """
        try:
            # Si no se especifican hojas, obtener todas las hojas del spreadsheet
            if nombres_hojas is None:
                nombres_hojas = [worksheet.title for worksheet in spreadsheet.worksheets()]
            
            for nombre_hoja in nombres_hojas:
                try:
                    worksheet = spreadsheet.worksheet(nombre_hoja)
                    GoogleSheetsService.aplicar_formato(
                        worksheet, 
                        formato_personalizado=formato_personalizado,
                        ajustar_columnas=ajustar_columnas,
                        limite_columnas=limite_columnas
                    )
                except Exception as e:
                    logger.error(f"Error al procesar la hoja {nombre_hoja}: {e}")
        except Exception as e:
            logger.error(f"Error al aplicar formato a las hojas: {e}")
            raise