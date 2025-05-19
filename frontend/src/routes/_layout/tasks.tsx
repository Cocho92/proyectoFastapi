import {  
    Container,  
    EmptyState,  
    Flex,  
    Heading,  
    Table,  
    VStack,  
  } from "@chakra-ui/react"  
  import { useQuery } from "@tanstack/react-query"  
  import { createFileRoute, useNavigate } from "@tanstack/react-router"  
  import { FiSearch } from "react-icons/fi"  
  import { z } from "zod"  
  import { TasksService } from "@/client"  
  import { TaskActionsMenu } from "@/components/Common/TaskActionsMenu"  
  import AddTask from "@/components/Tasks/AddTask"  
  import PendingTasks from "@/components/Pending/PendingTasks"  
  import {  
    PaginationItems,  
    PaginationNextTrigger,  
    PaginationPrevTrigger,  
    PaginationRoot,  
  } from "@/components/ui/pagination.tsx"  
    
  const tasksSearchSchema = z.object({  
    page: z.number().catch(1),  
  })  
    
  const PER_PAGE = 5  
    
  function getTasksQueryOptions({ page }: { page: number }) {  
    return {  
      queryFn: () =>  
        TasksService.readTasks({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),  
      queryKey: ["tasks", { page }],  
    }  
  }  
    
  export const Route = createFileRoute("/_layout/tasks")({  
    component: Tasks,  
    validateSearch: (search) => tasksSearchSchema.parse(search),  
  })  
    
  function TasksTable() {  
    const navigate = useNavigate({ from: Route.fullPath })  
    const { page } = Route.useSearch()  
    
    const { data, isLoading, isPlaceholderData } = useQuery({  
      ...getTasksQueryOptions({ page }),  
      placeholderData: (prevData) => prevData,  
    })  
    
    const setPage = (page: number) =>  
      navigate({  
        search: (prev: { [key: string]: string }) => ({ ...prev, page }),  
      })  
    
    const tasks = data?.data.slice(0, PER_PAGE) ?? []  
    const count = data?.count ?? 0  
    
    if (isLoading) {  
      return <PendingTasks />  
    }  
    
    if (tasks.length === 0) {  
      return (  
        <EmptyState.Root>  
          <EmptyState.Content>  
            <EmptyState.Indicator>  
              <FiSearch />  
            </EmptyState.Indicator>  
            <VStack textAlign="center">  
              <EmptyState.Title>You don't have any tasks yet</EmptyState.Title>  
              <EmptyState.Description>  
                Add a new task to get started  
              </EmptyState.Description>  
            </VStack>  
          </EmptyState.Content>  
        </EmptyState.Root>  
      )  
    }  
    
    return (  
      <>  
        <Table.Root size={{ base: "sm", md: "md" }}>  
          <Table.Header>  
            <Table.Row>  
              <Table.ColumnHeader w="20%">ID</Table.ColumnHeader>  
              <Table.ColumnHeader w="20%">Title</Table.ColumnHeader>  
              <Table.ColumnHeader w="20%">Description</Table.ColumnHeader>  
              <Table.ColumnHeader w="15%">Status</Table.ColumnHeader>  
              <Table.ColumnHeader w="15%">Due Date</Table.ColumnHeader>  
              <Table.ColumnHeader w="10%">Actions</Table.ColumnHeader>  
            </Table.Row>  
          </Table.Header>  
          <Table.Body>  
            {tasks?.map((task) => (  
              <Table.Row key={task.id} opacity={isPlaceholderData ? 0.5 : 1}>  
                <Table.Cell truncate maxW="20%">  
                  {task.id}  
                </Table.Cell>  
                <Table.Cell truncate maxW="20%">  
                  {task.title}  
                </Table.Cell>  
                <Table.Cell  
                  color={!task.description ? "gray" : "inherit"}  
                  truncate  
                  maxW="20%"  
                >  
                  {task.description || "N/A"}  
                </Table.Cell>  
                <Table.Cell truncate maxW="15%">  
                  {task.status}  
                </Table.Cell>  
                <Table.Cell truncate maxW="15%">  
                  {task.due_date ? new Date(task.due_date).toLocaleDateString() : "N/A"}  
                </Table.Cell>  
                <Table.Cell width="10%">  
                  <TaskActionsMenu task={task} />  
                </Table.Cell>  
              </Table.Row>  
            ))}  
          </Table.Body>  
        </Table.Root>  
        <Flex justifyContent="flex-end" mt={4}>  
          <PaginationRoot  
            count={count}  
            pageSize={PER_PAGE}  
            onPageChange={({ page }) => setPage(page)}  
          >  
            <Flex>  
              <PaginationPrevTrigger />  
              <PaginationItems />  
              <PaginationNextTrigger />  
            </Flex>  
          </PaginationRoot>  
        </Flex>  
      </>  
    )  
  }  
    
  function Tasks() {  
    return (  
      <Container maxW="full">  
        <Heading size="lg" pt={12}>  
          Tasks Management  
        </Heading>  
        <AddTask />  
        <TasksTable />  
      </Container>  
    )  
  }