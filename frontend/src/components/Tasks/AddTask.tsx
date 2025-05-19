// import { useMutation, useQueryClient } from "@tanstack/react-query"  
// import { type SubmitHandler, useForm,Controller } from "react-hook-form"  
  
// import {  
//   Button,  
//   DialogActionTrigger,  
//   DialogTitle,  
//   Input,  
//   Text,  
//   VStack,  
//   Select, // Importado directamente como Select
// } from "@chakra-ui/react"  
// import { useState } from "react"  
// import { FaPlus } from "react-icons/fa"  
  
// import { type TaskCreate, TasksService } from "@/client"  
// import type { ApiError } from "@/client/core/ApiError"  
// import useCustomToast from "@/hooks/useCustomToast"  
// import { handleError } from "@/utils"  
// import {  
//   DialogBody,  
//   DialogCloseTrigger,  
//   DialogContent,  
//   DialogFooter,  
//   DialogHeader,  
//   DialogRoot,  
//   DialogTrigger,  
// } from "../ui/dialog"  
// import { Field } from "../ui/field"  
  
// const AddTask = () => {  
//   const [isOpen, setIsOpen] = useState(false)  
//   const queryClient = useQueryClient()  
//   const { showSuccessToast } = useCustomToast()  
//   const {  
//     register,  
//     handleSubmit,  
//     reset,
//     control,  
//     formState: { errors, isValid, isSubmitting },  
//   } = useForm<TaskCreate>({  
//     mode: "onBlur",  
//     criteriaMode: "all",  
//     defaultValues: {  
//       title: "",  
//       description: "",  
//       status: "pending",  
//       due_date: null,  
//     },  
//   })  
  
//   const mutation = useMutation({  
//     mutationFn: (data: TaskCreate) =>  
//       TasksService.createTask({ requestBody: data }),  
//     onSuccess: () => {  
//       showSuccessToast("Task created successfully.")  
//       reset()  
//       setIsOpen(false)  
//     },  
//     onError: (err: ApiError) => {  
//       handleError(err)  
//     },  
//     onSettled: () => {  
//       queryClient.invalidateQueries({ queryKey: ["tasks"] })  
//     },  
//   })  
  
//   const onSubmit: SubmitHandler<TaskCreate> = (data) => {  
//     mutation.mutate(data)  
//   }  
  
//   return (  
//     <DialogRoot  
//       size={{ base: "xs", md: "md" }}  
//       placement="center"  
//       open={isOpen}  
//       onOpenChange={({ open }) => setIsOpen(open)}  
//     >  
//       <DialogTrigger asChild>  
//         <Button value="add-task" my={4}>  
//           <FaPlus fontSize="16px" />  
//           Add Task  
//         </Button>  
//       </DialogTrigger>  
//       <DialogContent>  
//         <form onSubmit={handleSubmit(onSubmit)}>  
//           <DialogHeader>  
//             <DialogTitle>Add Task</DialogTitle>  
//           </DialogHeader>  
//           <DialogBody>  
//             <Text mb={4}>Fill in the details to add a new task.</Text>  
//             <VStack gap={4}>  
//               <Field  
//                 required  
//                 invalid={!!errors.title}  
//                 errorText={errors.title?.message}  
//                 label="Title"  
//               >  
//                 <Input  
//                   id="title"  
//                   {...register("title", {  
//                     required: "Title is required.",  
//                   })}  
//                   placeholder="Title"  
//                   type="text"  
//                 />  
//               </Field>  
  
//               <Field  
//                 invalid={!!errors.description}  
//                 errorText={errors.description?.message}  
//                 label="Description"  
//               >  
//                 <Input  
//                   id="description"  
//                   {...register("description")}  
//                   placeholder="Description"  
//                   type="text"  
//                 />  
//               </Field>  
  
//               <Field  
//                 invalid={!!errors.status}  
//                 errorText={errors.status?.message}  
//                 label="Status"  
//               >  
//                 {/*                  
//                 Select component replaced with native select
//                 Select component is not working as expected
//                  */}
//                 <Select id="status" {...register("status")} placeholder="Status">  
//                   <option value="pending">Pending</option>  
//                   <option value="in_progress">In Progress</option>  
//                   <option value="completed">Completed</option>  
//                 </Select>  
                 
//               </Field>  
  
//               <Field  
//                 invalid={!!errors.due_date}  
//                 errorText={errors.due_date?.message}  
//                 label="Due Date"  
//               >  
//                 <Input  
//                   id="due_date"  
//                   {...register("due_date")}  
//                   placeholder="Due Date"  
//                   type="datetime-local"  
//                 />  
//               </Field>  
//             </VStack>  
//           </DialogBody>  
  
//           <DialogFooter gap={2}>  
//             <DialogActionTrigger asChild>  
//               <Button  
//                 variant="subtle"  
//                 colorPalette="gray"  
//                 disabled={isSubmitting}  
//               >  
//                 Cancel  
//               </Button>  
//             </DialogActionTrigger>  
//             <Button  
//               variant="solid"  
//               type="submit"  
//               disabled={!isValid}  
//               loading={isSubmitting}  
//             >  
//               Save  
//             </Button>  
//           </DialogFooter>  
//         </form>  
//         <DialogCloseTrigger />  
//       </DialogContent>  
//     </DialogRoot>  
//   )  
// }  

// export default AddTask

// Solución con Controller para componentes controlados

// import { useMutation, useQueryClient } from "@tanstack/react-query"  
// import { type SubmitHandler, useForm, Controller } from "react-hook-form"  // Añadido Controller
  
// import {  
//   Button,  
//   DialogActionTrigger,  
//   DialogTitle,  
//   Input,  
//   Text,  
//   VStack,  
//   Select,  // Importamos Select normalmente
// } from "@chakra-ui/react"  
// import { useState } from "react"  
// import { FaPlus } from "react-icons/fa"  
  
// import { type TaskCreate, TasksService } from "@/client"  
// import type { ApiError } from "@/client/core/ApiError"  
// import useCustomToast from "@/hooks/useCustomToast"  
// import { handleError } from "@/utils"  
// import {  
//   DialogBody,  
//   DialogCloseTrigger,  
//   DialogContent,  
//   DialogFooter,  
//   DialogHeader,  
//   DialogRoot,  
//   DialogTrigger,  
// } from "../ui/dialog"  
// import { Field } from "../ui/field"  
  
// const AddTask = () => {  
//   const [isOpen, setIsOpen] = useState(false)  
//   const queryClient = useQueryClient()  
//   const { showSuccessToast } = useCustomToast()  
//   const {  
//     register,  
//     handleSubmit,  
//     reset,  
//     control,  // Añadido control para usar con Controller
//     formState: { errors, isValid, isSubmitting },  
//   } = useForm<TaskCreate>({  
//     mode: "onBlur",  
//     criteriaMode: "all",  
//     defaultValues: {  
//       title: "",  
//       description: "",  
//       status: "pending",  
//       due_date: null,  
//     },  
//   })  
  
//   const mutation = useMutation({  
//     mutationFn: (data: TaskCreate) =>  
//       TasksService.createTask({ requestBody: data }),  
//     onSuccess: () => {  
//       showSuccessToast("Task created successfully.")  
//       reset()  
//       setIsOpen(false)  
//     },  
//     onError: (err: ApiError) => {  
//       handleError(err)  
//     },  
//     onSettled: () => {  
//       queryClient.invalidateQueries({ queryKey: ["tasks"] })  
//     },  
//   })  
  
//   const onSubmit: SubmitHandler<TaskCreate> = (data) => {  
//     mutation.mutate(data)  
//   }  
  
//   return (  
//     <DialogRoot  
//       size={{ base: "xs", md: "md" }}  
//       placement="center"  
//       open={isOpen}  
//       onOpenChange={({ open }) => setIsOpen(open)}  
//     >  
//       <DialogTrigger asChild>  
//         <Button value="add-task" my={4}>  
//           <FaPlus fontSize="16px" />  
//           Add Task  
//         </Button>  
//       </DialogTrigger>  
//       <DialogContent>  
//         <form onSubmit={handleSubmit(onSubmit)}>  
//           <DialogHeader>  
//             <DialogTitle>Add Task</DialogTitle>  
//           </DialogHeader>  
//           <DialogBody>  
//             <Text mb={4}>Fill in the details to add a new task.</Text>  
//             <VStack gap={4}>  
//               <Field  
//                 required  
//                 invalid={!!errors.title}  
//                 errorText={errors.title?.message}  
//                 label="Title"  
//               >  
//                 <Input  
//                   id="title"  
//                   {...register("title", {  
//                     required: "Title is required.",  
//                   })}  
//                   placeholder="Title"  
//                   type="text"  
//                 />  
//               </Field>  
  
//               <Field  
//                 invalid={!!errors.description}  
//                 errorText={errors.description?.message}  
//                 label="Description"  
//               >  
//                 <Input  
//                   id="description"  
//                   {...register("description")}  
//                   placeholder="Description"  
//                   type="text"  
//                 />  
//               </Field>  
  
//               <Field  
//                 invalid={!!errors.status}  
//                 errorText={errors.status?.message}  
//                 label="Status"  
//               >  
//                 {/* Usando Controller en lugar de register directamente */}
//                 <Controller
//                   name="status"
//                   control={control}
//                   render={({ field }) => (
//                     <Select id="status" placeholder="Status" {...field}>
//                       <option value="pending">Pending</option>
//                       <option value="in_progress">In Progress</option>
//                       <option value="completed">Completed</option>
//                     </Select>
//                   )}
//                 />
//               </Field>  
  
//               <Field  
//                 invalid={!!errors.due_date}  
//                 errorText={errors.due_date?.message}  
//                 label="Due Date"  
//               >  
//                 <Input  
//                   id="due_date"  
//                   {...register("due_date")}  
//                   placeholder="Due Date"  
//                   type="datetime-local"  
//                 />  
//               </Field>  
//             </VStack>  
//           </DialogBody>  
  
//           <DialogFooter gap={2}>  
//             <DialogActionTrigger asChild>  
//               <Button  
//                 variant="subtle"  
//                 colorPalette="gray"  
//                 disabled={isSubmitting}  
//               >  
//                 Cancel  
//               </Button>  
//             </DialogActionTrigger>  
//             <Button  
//               variant="solid"  
//               type="submit"  
//               disabled={!isValid}  
//               loading={isSubmitting}  
//             >  
//               Save  
//             </Button>  
//           </DialogFooter>  
//         </form>  
//         <DialogCloseTrigger />  
//       </DialogContent>  
//     </DialogRoot>  
//   )  
// }  

// export default AddTask

// import { useMutation, useQueryClient } from "@tanstack/react-query"  
// import { type SubmitHandler, useForm, Controller } from "react-hook-form"  
// import {  
//   Button,  
//   DialogActionTrigger,  
//   DialogTitle,  
//   Input,  
//   Text,  
//   VStack,  
//   Portal,
//   createListCollection,
//   Select,
// } from "@chakra-ui/react"  
// import { useState } from "react"  
// import { FaPlus } from "react-icons/fa"  
// import { type TaskCreate, TasksService } from "@/client"  
// import type { ApiError } from "@/client/core/ApiError"  
// import useCustomToast from "@/hooks/useCustomToast"  
// import { handleError } from "@/utils"  
// import {  
//   DialogBody,  
//   DialogCloseTrigger,  
//   DialogContent,  
//   DialogFooter,  
//   DialogHeader,  
//   DialogRoot,  
//   DialogTrigger,  
// } from "../ui/dialog"  
// import { Field } from "../ui/field"  

// // Creamos la colección de estados para el Select
// const taskStatuses = createListCollection({
//   items: [
//     { label: "Pending", value: "pending" },
//     { label: "In Progress", value: "in_progress" },
//     { label: "Completed", value: "completed" },
//   ],
// })

// const AddTask = () => {  
//   const [isOpen, setIsOpen] = useState(false)  
//   const queryClient = useQueryClient()  
//   const { showSuccessToast } = useCustomToast()  
//   const {  
//     register,  
//     handleSubmit,  
//     reset,  
//     control,
//     formState: { errors, isValid, isSubmitting },  
//   } = useForm<TaskCreate>({  
//     mode: "onBlur",  
//     criteriaMode: "all",  
//     defaultValues: {  
//       title: "",  
//       description: "",  
//       status: "pending",  
//       due_date: null,  
//     },  
//   })  
  
//   const mutation = useMutation({  
//     mutationFn: (data: TaskCreate) =>  
//       TasksService.createTask({ requestBody: data }),  
//     onSuccess: () => {  
//       showSuccessToast("Task created successfully.")  
//       reset()  
//       setIsOpen(false)  
//     },  
//     onError: (err: ApiError) => {  
//       handleError(err)  
//     },  
//     onSettled: () => {  
//       queryClient.invalidateQueries({ queryKey: ["tasks"] })  
//     },  
//   })  
  
//   const onSubmit: SubmitHandler<TaskCreate> = (data) => {  
//     mutation.mutate(data)  
//   }  
  
//   return (  
//     <DialogRoot  
//       size={{ base: "xs", md: "md" }}  
//       placement="center"  
//       open={isOpen}  
//       onOpenChange={({ open }) => setIsOpen(open)}  
//     >  
//       <DialogTrigger asChild>  
//         <Button value="add-task" my={4}>  
//           <FaPlus fontSize="16px" />  
//           Add Task  
//         </Button>  
//       </DialogTrigger>  
//       <DialogContent>  
//         <form onSubmit={handleSubmit(onSubmit)}>  
//           <DialogHeader>  
//             <DialogTitle>Add Task</DialogTitle>  
//           </DialogHeader>  
//           <DialogBody>  
//             <Text mb={4}>Fill in the details to add a new task.</Text>  
//             <VStack gap={4}>  
//               <Field  
//                 required  
//                 invalid={!!errors.title}  
//                 errorText={errors.title?.message}  
//                 label="Title"  
//               >  
//                 <Input  
//                   id="title"  
//                   {...register("title", {  
//                     required: "Title is required.",  
//                   })}  
//                   placeholder="Title"  
//                   type="text"  
//                 />  
//               </Field>  
  
//               <Field  
//                 invalid={!!errors.description}  
//                 errorText={errors.description?.message}  
//                 label="Description"  
//               >  
//                 <Input  
//                   id="description"  
//                   {...register("description")}  
//                   placeholder="Description"  
//                   type="text"  
//                 />  
//               </Field>  
  
//               <Field  
//                 invalid={!!errors.status}  
//                 errorText={errors.status?.message}  
//                 label="Status"  
//               >  
//                 <Controller
//                   control={control}
//                   name="status"
//                   render={({ field }) => (
//                     <Select.Root
//                       name={field.name}
//                       value={field.value}
//                       onValueChange={({ value }) => field.onChange(value)}
//                       onInteractOutside={() => field.onBlur()}
//                       collection={taskStatuses}
//                     >
//                       <Select.HiddenSelect />
//                       <Select.Control>
//                         <Select.Trigger>
//                           <Select.ValueText placeholder="Select status" />
//                         </Select.Trigger>
//                         <Select.IndicatorGroup>
//                           <Select.Indicator />
//                         </Select.IndicatorGroup>
//                       </Select.Control>
//                       <Portal>
//                         <Select.Positioner>
//                           <Select.Content>
//                             {taskStatuses.items.map((status) => (
//                               <Select.Item item={status} key={status.value}>
//                                 {status.label}
//                                 <Select.ItemIndicator />
//                               </Select.Item>
//                             ))}
//                           </Select.Content>
//                         </Select.Positioner>
//                       </Portal>
//                     </Select.Root>
//                   )}
//                 />
//               </Field>  
  
//               <Field  
//                 invalid={!!errors.due_date}  
//                 errorText={errors.due_date?.message}  
//                 label="Due Date"  
//               >  
//                 <Input  
//                   id="due_date"  
//                   {...register("due_date")}  
//                   placeholder="Due Date"  
//                   type="datetime-local"  
//                 />  
//               </Field>  
//             </VStack>  
//           </DialogBody>  
  
//           <DialogFooter gap={2}>  
//             <DialogActionTrigger asChild>  
//               <Button  
//                 variant="subtle"  
//                 colorPalette="gray"  
//                 disabled={isSubmitting}  
//               >  
//                 Cancel  
//               </Button>  
//             </DialogActionTrigger>  
//             <Button  
//               variant="solid"  
//               type="submit"  
//               disabled={!isValid}  
//               loading={isSubmitting}  
//             >  
//               Save  
//             </Button>  
//           </DialogFooter>  
//         </form>  
//         <DialogCloseTrigger />  
//       </DialogContent>  
//     </DialogRoot>  
//   )  
// }  

// export default AddTask

// Solución ajustada para trabajar con valores de tipo array
import { useMutation, useQueryClient } from "@tanstack/react-query"  
import { type SubmitHandler, useForm, Controller } from "react-hook-form"  
  
import {  
  Button,  
  DialogActionTrigger,  
  DialogTitle,  
  Input,  
  Text,  
  VStack,  
  Select,
  Portal,
  createListCollection,
} from "@chakra-ui/react"  
import { useState } from "react"  
import { FaPlus } from "react-icons/fa"  
  
import { type TaskCreate, TasksService } from "@/client"  
import type { ApiError } from "@/client/core/ApiError"  
import useCustomToast from "@/hooks/useCustomToast"  
import { handleError } from "@/utils"  
import {  
  DialogBody,  
  DialogCloseTrigger,  
  DialogContent,  
  DialogFooter,  
  DialogHeader,  
  DialogRoot,  
  DialogTrigger,  
} from "../ui/dialog"  
import { Field } from "../ui/field"  

// Crear colección para los estados
const statusCollection = createListCollection({
  items: [
    { label: "Pending", value: "pending" },
    { label: "In Progress", value: "in_progress" },
    { label: "Completed", value: "completed" },
  ],
})

// Modificar el tipo TaskCreate para incluir el array
type ModifiedTaskCreate = Omit<TaskCreate, 'status'> & {
  status: string | string[]
}

const AddTask = () => {  
  const [isOpen, setIsOpen] = useState(false)  
  const queryClient = useQueryClient()  
  const { showSuccessToast } = useCustomToast()  
  const {  
    register,  
    handleSubmit,  
    reset,  
    control,  
    formState: { errors, isValid, isSubmitting },  
  } = useForm<ModifiedTaskCreate>({  
    mode: "onBlur",  
    criteriaMode: "all",  
    defaultValues: {  
      title: "",  
      description: "",  
      status: ["pending"], // Cambiado a array
      due_date: null,  
    },  
  })  
  
  const mutation = useMutation({  
    mutationFn: (data: ModifiedTaskCreate) => {
      // Convertir el status de array a string antes de enviar
      const apiData = {
        ...data,
        status: Array.isArray(data.status) ? data.status[0] : data.status
      } as TaskCreate;
      
      return TasksService.createTask({ requestBody: apiData });
    },  
    onSuccess: () => {  
      showSuccessToast("Task created successfully.")  
      reset()  
      setIsOpen(false)  
    },  
    onError: (err: ApiError) => {  
      handleError(err)  
    },  
    onSettled: () => {  
      queryClient.invalidateQueries({ queryKey: ["tasks"] })  
    },  
  })  
  
  const onSubmit: SubmitHandler<ModifiedTaskCreate> = (data) => {  
    mutation.mutate(data)  
  }  
  
  return (  
    <DialogRoot  
      size={{ base: "xs", md: "md" }}  
      placement="center"  
      open={isOpen}  
      onOpenChange={({ open }) => setIsOpen(open)}  
    >  
      <DialogTrigger asChild>  
        <Button value="add-task" my={4}>  
          <FaPlus fontSize="16px" />  
          Add Task  
        </Button>  
      </DialogTrigger>  
      <DialogContent>  
        <form onSubmit={handleSubmit(onSubmit)}>  
          <DialogHeader>  
            <DialogTitle>Add Task</DialogTitle>  
          </DialogHeader>  
          <DialogBody>  
            <Text mb={4}>Fill in the details to add a new task.</Text>  
            <VStack gap={4}>  
              <Field  
                required  
                invalid={!!errors.title}  
                errorText={errors.title?.message}  
                label="Title"  
              >  
                <Input  
                  id="title"  
                  {...register("title", {  
                    required: "Title is required.",  
                  })}  
                  placeholder="Title"  
                  type="text"  
                />  
              </Field>  
  
              <Field  
                invalid={!!errors.description}  
                errorText={errors.description?.message}  
                label="Description"  
              >  
                <Input  
                  id="description"  
                  {...register("description")}  
                  placeholder="Description"  
                  type="text"  
                />  
              </Field>  
  
              {/* <Field  
                invalid={!!errors.status}  
                errorText={errors.status?.message}  
                label="Status"  
              >  
                <Controller
                  name="status"
                  control={control}
                  render={({ field }) => (
                    <Select.Root
                      name={field.name}
                      value={Array.isArray(field.value) ? field.value : [field.value].filter(Boolean)}
                      onValueChange={({ value }) => field.onChange(value)}
                      onInteractOutside={() => field.onBlur()}
                      collection={statusCollection}
                    >
                      <Select.HiddenSelect />
                      <Select.Control>
                        <Select.Trigger>
                          <Select.ValueText placeholder="Select status" />
                        </Select.Trigger>
                        <Select.IndicatorGroup>
                          <Select.Indicator />
                        </Select.IndicatorGroup>
                      </Select.Control>
                      <Portal>
                        <Select.Positioner>
                          <Select.Content>
                            {statusCollection.items.map((status) => (
                              <Select.Item item={status} key={status.value}>
                                {status.label}
                                <Select.ItemIndicator />
                              </Select.Item>
                            ))}
                          </Select.Content>
                        </Select.Positioner>
                      </Portal>
                    </Select.Root>
                  )}
                />
              </Field>   */}
  
              <Field  
                invalid={!!errors.due_date}  
                errorText={errors.due_date?.message}  
                label="Due Date"  
              >  
                <Input  
                  id="due_date"  
                  {...register("due_date")}  
                  placeholder="Due Date"  
                  type="datetime-local"  
                />  
              </Field>  
            </VStack>  
          </DialogBody>  
  
          <DialogFooter gap={2}>  
            <DialogActionTrigger asChild>  
              <Button  
                variant="subtle"  
                colorPalette="gray"  
                disabled={isSubmitting}  
              >  
                Cancel  
              </Button>  
            </DialogActionTrigger>  
            <Button  
              variant="solid"  
              type="submit"  
              disabled={!isValid}  
              loading={isSubmitting}  
            >  
              Save  
            </Button>  
          </DialogFooter>  
        </form>  
        <DialogCloseTrigger />  
      </DialogContent>  
    </DialogRoot>  
  )  
}  

export default AddTask  