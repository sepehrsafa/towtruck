from fastapi import APIRouter, HTTPException, Security
from app.models import UserAccount
from app.models import Accident as AccidentModel
from app.models import AccidentChat as AccidentChatModel
from app.schemas.accident import (
    Accident,
    AddChat,
    AccidentChat,
    AccidentChats,
)
from typing import Annotated
from app.services.auth.utils import get_current_user

from app.utils.response import responses
from app.utils.exception import TowTruckException


chat_router = APIRouter(
    tags=["Accident Chat"],
)


@chat_router.post(
    "/{accident_id}/chat", response_model=AccidentChat, responses=responses
)
async def add_chat(
    accident_id: int,
    data: AddChat,
    current_user: UserAccount = Security(get_current_user),
):
    """
    Add a chat message to an accident.
    """

    accident = await AccidentModel.get_or_none(id=accident_id)
    if not accident:
        raise HTTPException(status_code=404, detail="Accident not found")

    chat = await AccidentChatModel.create(
        accident=accident, user=current_user, message=data.message
    )

    chat = await AccidentChatModel.get(id=chat.id).prefetch_related("user")
    return chat


@chat_router.get(
    "/{accident_id}/chat", response_model=AccidentChats, responses=responses
)
async def get_chats(
    accident_id: int, current_user: UserAccount = Security(get_current_user)
):
    """
    Returns all chat messages for an accident.
    """

    accident = await AccidentModel.get_or_none(id=accident_id)
    if not accident:
        raise HTTPException(status_code=404, detail="Accident not found")

    chats = await AccidentChatModel.filter(accident=accident).prefetch_related("user")
    return {"chats": chats}
