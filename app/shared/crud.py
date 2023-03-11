from sqlalchemy import select
from sqlalchemy.orm import joinedload

from auth.models import User
from shared.db import async_session

"""
Ошибка возникает из-за того, что вы пытаетесь получить доступ к dialogs атрибуту экземпляра User после того, как он был отключен от сеанса.

Когда вы вызываете session.merge(user)функцию get_user, в сеансе создается новый экземпляр User, который затем возвращается функцией. 
Однако любые последующие попытки доступа к атрибутам этого экземпляра, основанным на отложенной загрузке, например dialogs, завершатся неудачей, поскольку экземпляр больше не подключен к сеансу.

Чтобы исправить это, вы можете загрузить dialogs отношения с нетерпением, указав joinedloadв своем запросе, например:

result = await session.execute(select(User).options(joinedload(User.dialogs)).where(User.id == pk))

Или вы можете убедиться, что dialogs связь загружается до того, как User экземпляр будет отключен от сеанса, например, используя опцию with_relationships при вызове session.expunge():

user = await session.merge(user, load=False)
session.expunge(user, options=[sa.orm.joinedload('dialogs')])
Это обеспечит dialogs загрузку отношения и его доступность в User экземпляре даже после его отключения от сеанса.
"""


async def get_user(pk):
    async with async_session() as session:
        result = await session.execute(select(User).options(joinedload(User.dialogs)).where(User.id == pk))
        # result = await session.execute(select(User).where(User.id == pk))
        user = result.scalars().first()
        await session.refresh(user)
        if not user:
            return None
        return user
