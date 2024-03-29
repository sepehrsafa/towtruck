from fastapi import APIRouter, HTTPException, Security
from app.models import UserAccount
from app.models import Accident as AccidentModel
from app.models import Station as StationModel
from app.models import AccidentStatus
from app.schemas.accident import (
    ReportAccident,
    Accident,
    AddChat,
    AccidentChat,
    AccidentChats,
    Accidents,
    StatusUpdate,
)
from typing import Annotated
from app.services.auth.utils import get_current_user

from app.utils.response import responses
from app.utils.exception import TowTruckException
from app.queue import get_channel, check_if_assign_is_possible

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
        ).prefetch_related("reported_by", "assigned_to", "assigned_station")
    else:
        accidents = await AccidentModel.filter(
            assigned_to=current_user
        ).prefetch_related("reported_by", "assigned_to", "assigned_station")

    return {"accidents": accidents}


@router.get("/all", response_model=Accidents, responses=responses)
async def get_all_accidents(current_user: UserAccount = Security(get_current_user)):
    """
    Returns all accidents.
    """

    accidents = await AccidentModel.all().prefetch_related(
        "reported_by", "assigned_to", "assigned_station"
    )
    return {"accidents": accidents}


@router.get("/{accident_id}", response_model=Accident, responses=responses)
async def get_accident(
    accident_id: int, current_user: UserAccount = Security(get_current_user)
):
    """
    Returns a specific accident.
    """

    accident = await AccidentModel.get_or_none(id=accident_id).prefetch_related(
        "reported_by", "assigned_to", "assigned_station"
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

    station = await StationModel.get_or_none(id=data.assigned_station)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    accident = await AccidentModel.create(
        location=data.location,
        description=data.description,
        reported_by=current_user,
        assigned_station=station,
    )

    accident = await AccidentModel.get(id=accident.id).prefetch_related(
        "reported_by", "assigned_to", "assigned_station"
    )

    get_channel().basic_publish(
        exchange="", routing_key=f"station_{station.id}_queue", body=f"{accident.id}"
    )

    await check_if_assign_is_possible(station.id)

    return accident


# delete accident
@router.delete("/{accident_id}", response_model=Accident, responses=responses)
async def delete_accident(
    accident_id: int, current_user: UserAccount = Security(get_current_user)
):
    """
    Delete an accident.
    """
    accident = await AccidentModel.get_or_none(id=accident_id)
    if not accident:
        raise HTTPException(status_code=404, detail="Accident not found")

    await accident.delete()
    return accident


# update accident status
@router.put("/{accident_id}/status", response_model=Accident, responses=responses)
async def update_accident_status(
    accident_id: int,
    status: StatusUpdate,
    current_user: UserAccount = Security(get_current_user),
):
    """
    Update an accident's status.
    """

    accident = await AccidentModel.get_or_none(id=accident_id)
    if not accident:
        raise HTTPException(status_code=404, detail="Accident not found")

    accident.status = status.status
    await accident.save()

    print(f"Updated accident {accident.id} status to {status.status}")

    if accident.status == AccidentStatus.COMPLETED and accident.assigned_to_id is not None:
        print("Unassigning user from accident")
        user = await UserAccount.get(pk=accident.assigned_to_id)
        user.is_user_on_duty = False
        await user.save()

    await check_if_assign_is_possible(accident.assigned_station_id)

    accident = await AccidentModel.get(id=accident.id).prefetch_related(
        "reported_by", "assigned_to", "assigned_station"
    )
    return accident
