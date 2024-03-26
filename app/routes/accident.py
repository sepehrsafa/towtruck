from fastapi import APIRouter, HTTPException, Security
from app.models import UserAccount
from app.models import Accident as AccidentModel
from app.schemas.accident import (
    ReportAccident,
    Accident,
    AddChat,
    AccidentChat,
    AccidentChats,
    Accidents,
)
from typing import Annotated
from app.services.auth.utils import get_current_user

from app.utils.response import responses
from app.utils.exception import TowTruckException

router = APIRouter(
    tags=["Accident"],
)


@router.get("/", response_model=Accidents, responses=responses)
async def get_accidents(current_user: UserAccount = Security(get_current_user)):
    """
    Returns all accidents reported by the current user or assigned to the current user.
    """

    if current_user.type == "HQ_EMPLOYEE":
        accidents = await AccidentModel.filter(
            reported_by=current_user
        ).prefetch_related("reported_by", "assigned_to")
    else:
        accidents = await AccidentModel.filter(
            assigned_to=current_user
        ).prefetch_related("reported_by", "assigned_to")

    return {"accidents": accidents}


@router.get("/all", response_model=Accidents, responses=responses)
async def get_all_accidents(current_user: UserAccount = Security(get_current_user)):
    """
    Returns all accidents.
    """

    accidents = await AccidentModel.all().prefetch_related("reported_by", "assigned_to")
    return {"accidents": accidents}


@router.get("/{accident_id}", response_model=Accident, responses=responses)
async def get_accident(
    accident_id: int, current_user: UserAccount = Security(get_current_user)
):
    """
    Returns a specific accident.
    """

    accident = await AccidentModel.get_or_none(id=accident_id).prefetch_related(
        "reported_by", "assigned_to"
    )
    if not accident:
        raise HTTPException(status_code=404, detail="Accident not found")

    return accident


@router.post("/report", response_model=Accident, responses=responses)
async def report_accident(
    data: ReportAccident, current_user: UserAccount = Security(get_current_user)
):
    """
    Report an accident.
    """
    accident = await AccidentModel.create(
        location=data.location,
        description=data.description,
        reported_by=current_user,
    )

    accident = await AccidentModel.get(id=accident.id).prefetch_related(
        "reported_by", "assigned_to"
    )
    return accident
