import {  
    Button,  
    ButtonGroup,  
    DialogActionTrigger,  
    Input,  
    Text,  
    VStack,  
    Select,  
  } from "@chakra-ui/react"  
  import { useMutation, useQueryClient } from "@tanstack/react-query"  
  import { useState } from "react"  
  import { type SubmitHandler, useForm } from "react-hook-form"  
  import { FaExchangeAlt } from "react-icons/fa"  
    
  import { type ApiError, type TaskPublic, TasksService } from "@/client"  
  import useCustomToast from "@/hooks/useCustomToast"  
  import { handleError } from "@/utils"  
  import {  
    DialogBody,  
    DialogCloseTrigger,  
    DialogContent,  
    DialogFooter,  
    DialogHeader,  
    DialogRoot,  
    DialogTitle,  
    DialogTrigger,  
  } from "../ui/dialog"  
  import { Field } from "../ui/field"  
    
  interface EditTaskProps {  
    task: TaskPublic  
  }  
    
  interface TaskUpdateForm {  
    title?: string  
    description?: string  
    status?: string  
    due_date?: string  
  }  
    
  const EditTask = ({ task }: EditTaskProps) => {  
    const [isOpen, setIsOpen] = useState(false)  
    const queryClient = useQueryClient()  
    const { showSuccessToast } = useCustomToast()  
    const {  
      register,  
      handleSubmit,  
      reset,  
      formState: { errors, isSubmitting },  
    } = useForm<TaskUpdateForm>({  
      mode: "onBlur",  
      criteriaMode: "all",  
      defaultValues: {  
        ...task,  
        description: task.description ?? undefined,  
        due_date: task.due_date ? new Date(task.due_date).toISOString().slice(0, 16) : undefined,  
      },  
    })  
    
    const mutation = useMutation({  
      mutationFn: (data: TaskUpdateForm) =>  
        TasksService.updateTask({ id: task.id, requestBody: data }),  
      onSuccess: () => {  
        showSuccessToast("Task updated successfully.")  
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
    
    const onSubmit: SubmitHandler<TaskUpdateForm> = async (data) => {  
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
          <Button variant="ghost">  
            <FaExchangeAlt fontSize="16px" />  
            Edit Task  
          </Button>  
        </DialogTrigger>  
        <DialogContent>  
          <form onSubmit={handleSubmit(onSubmit)}>  
            <DialogHeader>  
              <DialogTitle>Edit Task</DialogTitle>  
            </DialogHeader>  
            <DialogBody>  
              <Text mb={4}>Update the task details below.</Text>  
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
                      required: "Title is required",  
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
                  <Select  
                    id="status"  
                    {...register("status")}  
                    placeholder="Status"  
                  >  
                    <option value="pending">Pending</option>  
                    <option value="in_progress">In Progress</option>  
                    <option value="completed">Completed</option>  
                  </Select>  
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
              <ButtonGroup>  
                <DialogActionTrigger asChild>  
                  <Button  
                    variant="subtle"  
                    colorPalette="gray"  
                    disabled={isSubmitting}  
                  >  
                    Cancel  
                  </Button>  
                </DialogActionTrigger>  
                <Button variant="solid" type="submit" loading={isSubmitting}>  
                  Save  
                </Button>  
              </ButtonGroup>  
            </DialogFooter>  
          </form>  
          <DialogCloseTrigger />  
        </DialogContent>  
      </DialogRoot>  
    )  
  }  
    
  export default EditTask