from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session

from chat.models.dialog import DialogParticipant
from client.models import Device


def get_clients_not_currently_in_dialog(session: Session, dialog_id: int, user_id: int, current_devices: List[int]) -> List[int]:
    query = (
        session.query(
            Device.notification_token
        )
        .join(DialogParticipant, and_(Device.user_id == DialogParticipant.user_id, DialogParticipant.dialog_id == dialog_id))
        .filter(DialogParticipant.dialog_id == dialog_id)
        .filter(Device.id.notin_(current_devices))
        .filter(Device.notification_token.isnot(None))
        .filter(Device.user_id != user_id)
        .distinct()
        .all()
    )
    return [token[0] for token in query]
