from typing import TYPE_CHECKING, List

from fastapi import HTTPException
from starlette import status

from api.exams.schemas import SelectedAnswerData

if TYPE_CHECKING:
    from api.exams.service import ExamService


async def calculate_exam_score(
    exam_service: "ExamService",
    answers_data: List[SelectedAnswerData],
    quantity: int,
):
    if quantity == 0:
        return None

    correct_answers = 0
    for answer_data in answers_data:
        question_id = answer_data.question_id
        answer_id = answer_data.answer_id

        question = await exam_service.get_question_by_id(question_id)
        answer = await exam_service.get_answer_by_id(answer_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question {question_id} not found.",
            )
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Answer {answer_id} not found.",
            )
        correct_answer = await exam_service.get_correct_answer(answer_id, question)
        if correct_answer:
            correct_answers += 1

    percentage_correct = (correct_answers / quantity) * 100
    if percentage_correct < 30:
        return 2
    elif 40 <= percentage_correct < 70:
        return 3
    elif 70 <= percentage_correct < 90:
        return 4
    elif 90 <= percentage_correct <= 100:
        return 5
    else:
        return None
