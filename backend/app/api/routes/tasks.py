import uuid  
from typing import Any  
  
from fastapi import APIRouter, HTTPException  
from sqlmodel import func, select  
  
from app.api.deps import CurrentUser, SessionDep  
from app.models import Message, Task, TaskCreate, TaskPublic, TasksPublic, TaskUpdate, TaskAssignment, User  
  
router = APIRouter(prefix="/tasks", tags=["tasks"])  
  
@router.get("/", response_model=TasksPublic)  
def read_tasks(  
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100  
) -> Any:  
    """  
    Retrieve tasks.  
    """  
    if current_user.is_superuser:  
        count_statement = select(func.count()).select_from(Task)  
        count = session.exec(count_statement).one()  
        statement = select(Task).offset(skip).limit(limit)  
        tasks = session.exec(statement).all()  
    else:  
        # Get tasks owned by user or assigned to user  
        count_statement = (  
            select(func.count())  
            .select_from(Task)  
            .where(  
                (Task.owner_id == current_user.id) |   
                (Task.id.in_(  
                    select(TaskAssignment.task_id).where(TaskAssignment.user_id == current_user.id)  
                ))  
            )  
        )  
        count = session.exec(count_statement).one()  
        statement = (  
            select(Task)  
            .where(  
                (Task.owner_id == current_user.id) |   
                (Task.id.in_(  
                    select(TaskAssignment.task_id).where(TaskAssignment.user_id == current_user.id)  
                ))  
            )  
            .offset(skip)  
            .limit(limit)  
        )  
        tasks = session.exec(statement).all()  
      
    # Cargar los usuarios asignados a cada tarea  
    tasks_with_assignees = []  
    for task in tasks:  
        # Obtener asignaciones  
        assignments_statement = select(TaskAssignment).where(TaskAssignment.task_id == task.id)  
        assignments = session.exec(assignments_statement).all()  
          
        # Obtener usuarios asignados  
        assignees = []  
        for assignment in assignments:  
            user_statement = select(User).where(User.id == assignment.user_id)  
            user = session.exec(user_statement).first()  
            if user:  
                assignees.append(user)  
          
        # Crear una copia del task con los asignados  
        task_dict = task.model_dump()  
        task_dict["assignees"] = assignees  
        tasks_with_assignees.append(task_dict)  
      
    return TasksPublic(data=tasks_with_assignees, count=count)  
  
@router.post("/", response_model=TaskPublic)  
def create_task(  
    *, session: SessionDep, current_user: CurrentUser, task_in: TaskCreate  
) -> Any:  
    """  
    Create new task.  
    """  
    task = Task.model_validate(task_in, update={"owner_id": current_user.id})  
    session.add(task)  
    session.commit()  
    session.refresh(task)  
    return task  
  
@router.get("/{id}", response_model=TaskPublic)  
def read_task(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:  
    """  
    Get task by ID.  
    """  
    task = session.get(Task, id)  
    if not task:  
        raise HTTPException(status_code=404, detail="Task not found")  
      
    # Verificar si el usuario es propietario o está asignado a la tarea  
    if not current_user.is_superuser:  
        # Verificar si es propietario  
        is_owner = task.owner_id == current_user.id  
          
        # Verificar si está asignado  
        assignment_statement = select(TaskAssignment).where(  
            TaskAssignment.task_id == id,  
            TaskAssignment.user_id == current_user.id  
        )  
        is_assigned = session.exec(assignment_statement).first() is not None  
          
        if not (is_owner or is_assigned):  
            raise HTTPException(status_code=400, detail="Not enough permissions")  
      
    # Obtener asignados  
    assignments_statement = select(TaskAssignment).where(TaskAssignment.task_id == id)  
    assignments = session.exec(assignments_statement).all()  
      
    assignees = []  
    for assignment in assignments:  
        user_statement = select(User).where(User.id == assignment.user_id)  
        user = session.exec(user_statement).first()  
        if user:  
            assignees.append(user)  
      
    # Crear respuesta con asignados  
    task_dict = task.model_dump()  
    task_dict["assignees"] = assignees  
      
    return task_dict  
  
@router.put("/{id}", response_model=TaskPublic)  
def update_task(  
    *,  
    session: SessionDep,  
    current_user: CurrentUser,  
    id: uuid.UUID,  
    task_in: TaskUpdate,  
) -> Any:  
    """  
    Update a task.  
    """  
    task = session.get(Task, id)  
    if not task:  
        raise HTTPException(status_code=404, detail="Task not found")  
    if not current_user.is_superuser and (task.owner_id != current_user.id):  
        raise HTTPException(status_code=400, detail="Not enough permissions")  
      
    update_dict = task_in.model_dump(exclude_unset=True)  
    task.sqlmodel_update(update_dict)  
    session.add(task)  
    session.commit()  
    session.refresh(task)  
      
    # Obtener asignados para la respuesta  
    assignments_statement = select(TaskAssignment).where(TaskAssignment.task_id == id)  
    assignments = session.exec(assignments_statement).all()  
      
    assignees = []  
    for assignment in assignments:  
        user_statement = select(User).where(User.id == assignment.user_id)  
        user = session.exec(user_statement).first()  
        if user:  
            assignees.append(user)  
      
    # Crear respuesta con asignados  
    task_dict = task.model_dump()  
    task_dict["assignees"] = assignees  
      
    return task_dict  
  
@router.delete("/{id}", response_model=Message)  
def delete_task(  
    *,  
    session: SessionDep,  
    current_user: CurrentUser,  
    id: uuid.UUID,  
) -> Any:  
    """  
    Delete a task.  
    """  
    task = session.get(Task, id)  
    if not task:  
        raise HTTPException(status_code=404, detail="Task not found")  
    if not current_user.is_superuser and (task.owner_id != current_user.id):  
        raise HTTPException(status_code=400, detail="Not enough permissions")  
      
    session.delete(task)  
    session.commit()  
      
    return {"message": "Task deleted successfully"}  
  
@router.post("/{task_id}/assign/{user_id}", response_model=Message)  
def assign_user_to_task(  
    *,  
    session: SessionDep,  
    current_user: CurrentUser,  
    task_id: uuid.UUID,  
    user_id: uuid.UUID,  
) -> Any:  
    """  
    Assign a user to a task.  
    """  
    task = session.get(Task, task_id)  
    if not task:  
        raise HTTPException(status_code=404, detail="Task not found")  
      
    user = session.get(User, user_id)  
    if not user:  
        raise HTTPException(status_code=404, detail="User not found")  
      
    if not current_user.is_superuser and (task.owner_id != current_user.id):  
        raise HTTPException(status_code=400, detail="Not enough permissions")  
      
    # Verificar si ya existe la asignación  
    statement = select(TaskAssignment).where(  
        TaskAssignment.task_id == task_id,  
        TaskAssignment.user_id == user_id  
    )  
    existing = session.exec(statement).first()  
      
    if existing:  
        return {"message": "User already assigned to this task"}  
      
    # Crear nueva asignación  
    assignment = TaskAssignment(task_id=task_id, user_id=user_id)  
    session.add(assignment)  
    session.commit()  
      
    return {"message": "User assigned to task successfully"}  
  
@router.delete("/{task_id}/assign/{user_id}", response_model=Message)  
def remove_user_from_task(  
    *,  
    session: SessionDep,  
    current_user: CurrentUser,  
    task_id: uuid.UUID,  
    user_id: uuid.UUID,  
) -> Any:  
    """  
    Remove a user assignment from a task.  
    """  
    task = session.get(Task, task_id)  
    if not task:  
        raise HTTPException(status_code=404, detail="Task not found")  
      
    if not current_user.is_superuser and (task.owner_id != current_user.id):  
        raise HTTPException(status_code=400, detail="Not enough permissions")  
      
    # Buscar la asignación  
    statement = select(TaskAssignment).where(  
        TaskAssignment.task_id == task_id,  
        TaskAssignment.user_id == user_id  
    )  
    assignment = session.exec(statement).first()  
      
    if not assignment:  
        raise HTTPException(status_code=404, detail="Assignment not found")  
      
    # Eliminar la asignación  
    session.delete(assignment)  
    session.commit()  
      
    return {"message": "User removed from task successfully"}