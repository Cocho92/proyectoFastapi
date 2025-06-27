import { useState } from "react"  
import { Box, Button, Input } from "@chakra-ui/react"
import { VStack } from "@chakra-ui/layout"
import { NumberInput, NumberInputField, NumberInputStepper, NumberIncrementStepper, NumberDecrementStepper } from "@chakra-ui/number-input"
import { Checkbox } from "@chakra-ui/checkbox"
import { useToast } from "@chakra-ui/toast"
import { FormControl, FormLabel } from "@chakra-ui/form-control"
import { ErroresPamiService } from "@/client/sdk.gen"  
import { ExcelProcessResponse } from "@/client/types.gen"  
  
interface UploadExcelProps {  
  onProcessingComplete: (result: ExcelProcessResponse) => void  
}  
  
const UploadExcel = ({ onProcessingComplete }: UploadExcelProps) => {  
  const [file, setFile] = useState<File | null>(null)  
  const [spreadsheetKey, setSpreadsheetKey] = useState("")  
  const [columnaAProcesar, setColumnaAProcesar] = useState(0)  
  const [aplicarPatronesDefault, setAplicarPatronesDefault] = useState(true)  
  const [isLoading, setIsLoading] = useState(false)  
  const toast = useToast()  
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {  
    if (e.target.files && e.target.files.length > 0) {  
      setFile(e.target.files[0])  
    }  
  }  
  
  const handleSubmit = async (e: React.FormEvent) => {  
    e.preventDefault()  
    if (!file) {  
      toast({  
        title: "Error",  
        description: "Por favor seleccione un archivo Excel",  
        status: "error",  
        duration: 3000,  
        isClosable: true,  
      })  
      return  
    }  
  
    setIsLoading(true)  
    try {  
      const formData = { archivo: file }  
      const result = await ErroresPamiService.procesarExcel({  
        formData,  
        spreadsheetKey: spreadsheetKey || undefined,  
        columnaAProcesar,  
        aplicarPatronesDefault,  
      })  
        
      onProcessingComplete(result)  
      toast({  
        title: "Éxito",  
        description: "Archivo procesado correctamente",  
        status: "success",  
        duration: 3000,  
        isClosable: true,  
      })  
    } catch (error) {  
      toast({  
        title: "Error",  
        description: "Error al procesar el archivo",  
        status: "error",  
        duration: 3000,  
        isClosable: true,  
      })  
      console.error(error)  
    } finally {  
      setIsLoading(false)  
    }  
  }  
  
  return (  
    <Box as="form" onSubmit={handleSubmit}>  
      <VStack gap={4} alignItems="stretch">  
        <FormControl isRequired>  
          <FormLabel>Archivo Excel</FormLabel>  
          <Input type="file" accept=".xlsx,.xls" onChange={handleFileChange} />  
        </FormControl>  
          
        {/* <FormControl>  
          <FormLabel>ID de Google Spreadsheet (opcional)</FormLabel>  
          <Input   
            value={spreadsheetKey}   
            onChange={(e) => setSpreadsheetKey(e.target.value)}  
            placeholder="Dejar vacío para usar el predeterminado"  
          />  
        </FormControl>  
          
        <FormControl>  
          <FormLabel>Columna a procesar</FormLabel>  
          <NumberInput   
            min={0}   
            value={columnaAProcesar}   
            onChange={(_, value) => setColumnaAProcesar(value)}  
          >  
            <NumberInputField />  
            <NumberInputStepper>  
              <NumberIncrementStepper />  
              <NumberDecrementStepper />  
            </NumberInputStepper>  
          </NumberInput>  
        </FormControl>  
          
        <FormControl>  
          <Checkbox   
            isChecked={aplicarPatronesDefault}   
            onChange={(e) => setAplicarPatronesDefault(e.target.checked)}  
          >  
            Aplicar patrones predeterminados  
          </Checkbox>  
        </FormControl>   */}
          
        <Button   
          type="submit"   
          colorScheme="teal"   
          loading={isLoading}  
          loadingText="Procesando..."  
        >  
          Procesar Excel  
        </Button>  
      </VStack>  
    </Box>  
  )  
}  
  
export default UploadExcel