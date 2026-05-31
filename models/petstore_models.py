from pydantic import BaseModel
from typing import Optional, List


class Category(BaseModel):
    """Категория питомца"""
    id: Optional[int] = None
    name: Optional[str] = None


class Tag(BaseModel):
    """Тег питомца"""
    id: Optional[int] = None
    name: Optional[str] = None


class Pet(BaseModel):
    id: Optional[int] = None
    category: Optional[Category] = None
    name: Optional[str] = None
    photoUrls: Optional[List[str]] = None
    tags: Optional[List[Tag]] = None
    status: Optional[str] = None


class Order(BaseModel):
    """Модель заказа"""
    id: Optional[int] = None
    petId: int
    quantity: int
    shipDate: Optional[str] = None
    status: Optional[str] = None
    complete: bool = False


class User(BaseModel):
    """Модель пользователя"""
    id: Optional[int] = None
    username: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    userStatus: Optional[int] = None


class ApiResponse(BaseModel):
    """Стандартный ответ API"""
    code: Optional[int] = None
    type: Optional[str] = None
    message: Optional[str] = None
