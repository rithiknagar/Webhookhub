from sqlalchemy.ext.asyncio import AsyncSession

from webhookhub.core.security import  generate_api_key, get_key_prefix, hash_api_key
from webhookhub.db.models.api_key import APIKeyModel


async def create_api_key( session: AsyncSession, user_id, name: str, ) -> tuple[APIKeyModel, str]:

    api_key = generate_api_key()

    api_key_model = APIKeyModel(
        user_id=user_id,
        name=name,
        key_prefix=get_key_prefix(api_key),
        key_hash=hash_api_key(api_key),
    )

    session.add(api_key_model)

    await session.commit()
    await session.refresh(api_key_model)

    return api_key_model, api_key