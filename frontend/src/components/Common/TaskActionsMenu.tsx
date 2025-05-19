import { IconButton } from "@chakra-ui/react"  
import { BsThreeDotsVertical } from "react-icons/bs"  
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"  
  
import type { TaskPublic } from "@/client"  
import DeleteTask from "../Tasks/DeleteTask"  
import EditTask from "../Tasks/EditTask"  
  
interface TaskActionsMenuProps {  
  task: TaskPublic  
}  
  
export const TaskActionsMenu = ({ task }: TaskActionsMenuProps) => {  
  return (  
    <MenuRoot>  
      <MenuTrigger asChild>  
        <IconButton variant="ghost" color="inherit">  
          <BsThreeDotsVertical />  
        </IconButton>  
      </MenuTrigger>  
      <MenuContent>  
        <EditTask task={task} />  
        <DeleteTask id={task.id} />  
      </MenuContent>  
    </MenuRoot>  
  )  
}