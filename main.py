import json
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="问卷调查系统",
    description="一个简单的问卷调查后端系统，支持问卷创建、查询功能",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/surveys/", response_model=schemas.SurveyInDB, status_code=status.HTTP_201_CREATED)
def create_survey(survey: schemas.SurveyCreate, db: Session = Depends(get_db)):
    questions_json = json.dumps([q.model_dump() for q in survey.questions], ensure_ascii=False)
    db_survey = models.Survey(
        title=survey.title,
        description=survey.description,
        questions=questions_json
    )
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    
    questions_data = json.loads(db_survey.questions)
    return schemas.SurveyInDB(
        id=db_survey.id,
        title=db_survey.title,
        description=db_survey.description,
        questions=[schemas.Question(**q) for q in questions_data],
        created_at=db_survey.created_at,
        updated_at=db_survey.updated_at
    )

@app.get("/surveys/", response_model=List[schemas.SurveyInDB])
def get_surveys(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    surveys = db.query(models.Survey).offset(skip).limit(limit).all()
    result = []
    for survey in surveys:
        questions_data = json.loads(survey.questions)
        result.append(schemas.SurveyInDB(
            id=survey.id,
            title=survey.title,
            description=survey.description,
            questions=[schemas.Question(**q) for q in questions_data],
            created_at=survey.created_at,
            updated_at=survey.updated_at
        ))
    return result

@app.get("/surveys/{survey_id}", response_model=schemas.SurveyInDB)
def get_survey(survey_id: int, db: Session = Depends(get_db)):
    survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
    if survey is None:
        raise HTTPException(status_code=404, detail="问卷不存在")
    questions_data = json.loads(survey.questions)
    return schemas.SurveyInDB(
        id=survey.id,
        title=survey.title,
        description=survey.description,
        questions=[schemas.Question(**q) for q in questions_data],
        created_at=survey.created_at,
        updated_at=survey.updated_at
    )

@app.put("/surveys/{survey_id}", response_model=schemas.SurveyInDB)
def update_survey(survey_id: int, survey: schemas.SurveyUpdate, db: Session = Depends(get_db)):
    db_survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
    if db_survey is None:
        raise HTTPException(status_code=404, detail="问卷不存在")
    
    update_data = survey.model_dump(exclude_unset=True)
    if "questions" in update_data:
        update_data["questions"] = json.dumps([q.model_dump() for q in update_data["questions"]], ensure_ascii=False)
    
    for key, value in update_data.items():
        setattr(db_survey, key, value)
    
    db.commit()
    db.refresh(db_survey)
    
    questions_data = json.loads(db_survey.questions)
    return schemas.SurveyInDB(
        id=db_survey.id,
        title=db_survey.title,
        description=db_survey.description,
        questions=[schemas.Question(**q) for q in questions_data],
        created_at=db_survey.created_at,
        updated_at=db_survey.updated_at
    )

@app.delete("/surveys/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_survey(survey_id: int, db: Session = Depends(get_db)):
    db_survey = db.query(models.Survey).filter(models.Survey.id == survey_id).first()
    if db_survey is None:
        raise HTTPException(status_code=404, detail="问卷不存在")
    
    db.delete(db_survey)
    db.commit()
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
