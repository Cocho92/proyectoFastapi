import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    tasks: list["Task"] = Relationship(back_populates="owner", cascade_delete=True)  
    assigned_tasks: list["TaskAssignment"] = Relationship(back_populates="user", cascade_delete=True)

# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)



class ExcelProcessRequest(SQLModel):
    """Esquema de solicitud para procesar Excel"""
    spreadsheet_key: str
    columna_a_procesar: int = Field(0, description="Índice de la columna a procesar (0 es la primera)")
    aplicar_patrones_default: bool = Field(True, description="Si aplicar los patrones predefinidos")


class ProcessingStats(SQLModel):
    """Esquema para estadísticas de procesamiento"""
    registros_totales: int
    registros_criticos: int
    registros_a_revisar: int
    spreadsheet_title: str
    spreadsheet_url: str


class ExcelProcessResponse(SQLModel):
    """Esquema de respuesta del procesamiento"""
    mensaje: str
    archivo: str
    spreadsheet_key: str
    google_sheet_url: str


# Modelo base para Task
class TaskBase(SQLModel):  
    title: str = Field(min_length=1, max_length=255)  
    description: str | None = Field(default=None, max_length=255)  
    due_date: datetime | None = Field(default=None)  
    status: str = Field(default="pending", max_length=50)  # pending, in_progress, completed  

# Propiedades para crear un Task  
class TaskCreate(TaskBase):  
    pass  

# Propiedades para actualizar un Task
class TaskUpdate(TaskBase):  
    title: str | None = Field(default=None, min_length=1, max_length=255)  
    status: str | None = Field(default=None, max_length=50) 


# Modelo de base de datos
class Task(TaskBase, table=True):  
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)  
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")  
    owner: User | None = Relationship(back_populates="tasks")  
    assignees: list["TaskAssignment"] = Relationship(back_populates="task", cascade_delete=True)


# Modelo para asignar tareas a usuarios  
class TaskAssignment(SQLModel, table=True):  
    task_id: uuid.UUID = Field(foreign_key="task.id", primary_key=True, ondelete="CASCADE")  
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True, ondelete="CASCADE")  
    task: Task = Relationship(back_populates="assignees")  
    user: User = Relationship(back_populates="assigned_tasks")

# Propiedades para devolver vía API  
class TaskPublic(TaskBase):  
    id: uuid.UUID  
    owner_id: uuid.UUID  
    assignees: list[UserPublic] = []  


# Modelo para listar tareas  
class TasksPublic(SQLModel):  
    data: list[TaskPublic]  
    count: int