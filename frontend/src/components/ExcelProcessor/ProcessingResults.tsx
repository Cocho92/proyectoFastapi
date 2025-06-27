import { Box, Text, Link } from "@chakra-ui/react"  
import { ExcelProcessResponse } from "@/client/types.gen"  
import { FiExternalLink } from "react-icons/fi"  
import { VStack } from "@chakra-ui/layout"

interface ProcessingResultsProps {  
  result: ExcelProcessResponse  
}  
  
const ProcessingResults = ({ result }: ProcessingResultsProps) => {  
  return (  
    <Box mt={6} p={4} borderWidth="1px" borderRadius="lg">  
      <VStack alignItems="stretch" gap={3}>  
        <Text fontWeight="bold">{result.mensaje}</Text>  
        <Text>Archivo: {result.archivo}</Text>  
        <Box>  
          <Text>Ver resultados en Google Sheets:</Text>  
          <Link href={result.google_sheet_url} target="_blank" rel="noopener noreferrer" color="teal.500">  
            Abrir Google Sheet <FiExternalLink style={{ display: 'inline', marginLeft: '2px' }} />  
          </Link>  
        </Box>  
      </VStack>  
    </Box>  
  )  
}  
  
export default ProcessingResults