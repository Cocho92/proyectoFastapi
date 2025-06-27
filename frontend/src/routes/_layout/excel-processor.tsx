import { createFileRoute } from "@tanstack/react-router"  
import ExcelDashboard from "@/components/ExcelProcessor/ExcelDashboard"  
import {Container} from "@chakra-ui/react"
export const Route = createFileRoute("/_layout/excel-processor")({  
  component: ExcelProcessorPage,  
})  
  
function ExcelProcessorPage() {  
  return (
  <Container maxW="full">
    <ExcelDashboard />  
  </Container>
  )
}