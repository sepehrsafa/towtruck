from fastapi import APIRouter, HTTPException, Security
from app.models import UserAccount
from app.models import Station as StationModel
from app.schemas.accident import (
    Station,
    CreateStation,
    StationResponse,
    StationsResponse,
)
from typing import Annotated
from app.services.auth.utils import get_current_user

from app.utils.response import responses
from app.utils.exception import TowTruckException
from app.queue import channel

# Declare a queue (if it doesn't exist, it will be created)


router = APIRouter(
    tags=["Station"],
)

# do CURD operations here


@router.post("", response_model=StationResponse, responses=responses)
async def create_station(
    data: CreateStation,
    current_user: UserAccount = Security(get_current_user),
):
    """
    Create a new station.
    """

    station = await StationModel.create(**data.dict())

    station = (
        await StationModel.all().filter(id=station.id).first().prefetch_related("users")
    )

    channel.queue_declare(queue=f"station_{station.id}_queue")

    return station


@router.get("", response_model=StationsResponse, responses=responses)
async def get_stations(current_user: UserAccount = Security(get_current_user)):
    """
    Returns all stations.
    """

    stations = await StationModel.all().prefetch_related("users")
    return {"stations": stations}


@router.get("/{station_id}", response_model=StationResponse, responses=responses)
async def get_station(
    station_id: int, current_user: UserAccount = Security(get_current_user)
):
    """
    Returns a single station.
    """

    station = await StationModel.get_or_none(id=station_id).prefetch_related("users")
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    return station


@router.put("/{station_id}", response_model=StationResponse, responses=responses)
async def update_station(
    station_id: int,
    data: CreateStation,
    current_user: UserAccount = Security(get_current_user),
):
    """
    Update a station.
    """

    station = await StationModel.get_or_none(id=station_id).prefetch_related("users")
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    await station.update_from_dict(data.dict()).save()

    return station


@router.delete("/{station_id}", response_model=StationResponse, responses=responses)
async def delete_station(
    station_id: int,
    current_user: UserAccount = Security(get_current_user),
):
    """
    Delete a station.
    """

    station = await StationModel.get_or_none(id=station_id).prefetch_related("users")
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    await station.delete()

    # Delete the queue
    channel.queue_delete(queue=f"station_{station_id}_queue")

    return station
