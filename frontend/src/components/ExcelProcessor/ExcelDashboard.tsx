import { Box, Heading } from "@chakra-ui/react"  
import UploadExcel from "./UploadExcel"  
import ProcessingResults from "./ProcessingResults"  
import { useState } from "react"  
import { ExcelProcessResponse } from "@/client/types.gen"  
  
const ExcelDashboard = () => {  
  const [processingResult, setProcessingResult] = useState<ExcelProcessResponse | null>(null)  
    
  return (  
    <Box>  
      <Heading size="md" mb={4}>Deteccion Errores PAMI</Heading>  
      <UploadExcel onProcessingComplete={setProcessingResult} />  
      {processingResult && <ProcessingResults result={processingResult} />}  
    </Box>  
  )  
}  
  
export default ExcelDashboard