from fastapi import APIRouter, HTTPException, status
from models import ErrorResponse, SalaryCapResponse

router = APIRouter()

SALARY_CAP = 187895000


@router.get(
    "/salary_cap",
    response_model=SalaryCapResponse,
    responses={500: {"model": ErrorResponse}},
)
async def get_salary_cap():
    try:
        return SalaryCapResponse(salary_cap=SALARY_CAP)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
