import sys

import asyncio
from getpass import getpass

from sqlalchemy import select

from shopapi.core.security import hash_password
from shopapi.db.session import new_session
from shopapi.models import UserModel
from shopapi.models.enums import UserRole

# --- исправление для Windows ---
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# -------------------------------

async def create_admin():
    email = input("Admin email: ").strip()
    password = getpass("Admin password: ")

    if not email or not password:
        print("Email and password are required")
        return

    async with new_session() as session:
        query = select(UserModel).where(UserModel.email == email)
        result = await session.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("User with this email already exists")
            return

        admin = UserModel(
            email=email,
            password_hash=hash_password(password=password),
            role=UserRole.ADMIN,
        )

        session.add(admin)
        await session.commit()

        print(f"Admin {email} successfully created")

if __name__ == "__main__":
    asyncio.run(create_admin())