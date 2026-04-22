from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field

class Question(BaseModel):
    id: int = Field(..., description="问题ID")
    type: str = Field(..., description="问题类型：text, single_choice, multiple_choice")
    title: str = Field(..., description="问题标题")
    options: Optional[List[str]] = Field(None, description="选项列表，仅用于选择题")
    required: bool = Field(default=True, description="是否必填")

class SurveyCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="问卷标题")
    description: Optional[str] = Field(None, max_length=500, description="问卷描述")
    questions: List[Question] = Field(..., min_items=1, description="问题列表")

class SurveyUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    questions: Optional[List[Question]] = None

class SurveyInDB(BaseModel):
    id: int
    title: str
    description: Optional[str]
    questions: List[Question]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
