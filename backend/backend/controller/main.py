import logging
import json
import re
import os
import shutil


from fastapi.responses import JSONResponse
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from beanie import PydanticObjectId
from uuid import uuid4 as uuid
from uuid import UUID
import bcrypt
from fastapi.encoders import jsonable_encoder

from backend.models.User import User
from backend.models.Token import Token

from backend.security.jsonwebtoken import generate_jwt_token
from backend.config import main as config

from backend.controller.agent import run_agent as agent_run


async def signup(signup_data):
    is_user_already_exists = await User.find_one({"email": signup_data.email})

    if is_user_already_exists:
        return JSONResponse(
            {"success": False, "message": "User already exists"}, status_code=400
        )

    hashed_password = bcrypt.hashpw(
        signup_data.password.encode("utf-8"), bcrypt.gensalt()
    )

    new_user = User(
        name=signup_data.name,
        email=signup_data.email,
        password=hashed_password.decode("utf-8"),
    )

    await new_user.save()

    return JSONResponse(
        {
            "success": True,
            "message": "User created successfully",
            "navigate": "/signin",
            "user": {
                "name": new_user.name,
                "email": new_user.email,
                "id": str(new_user.id),
            },
        },
        status_code=201,
    )


async def signin(signin_data):
    user = await User.find_one({"email": signin_data.email})

    if not user:
        return JSONResponse(
            {"success": False, "message": "User not found"}, status_code=404
        )

    if not bcrypt.checkpw(
        signin_data.password.encode("utf-8"), user.password.encode("utf-8")
    ):
        return JSONResponse(
            {"success": False, "message": "Invalid password"}, status_code=400
        )

    session_id = str(uuid())
    access_token = generate_jwt_token(
        {"_id": str(user.id), "session_id": session_id, "mode": ""}, "access"
    )
    refresh_token = generate_jwt_token(
        {"_id": str(user.id), "session_id": session_id, "mode": ""}, "refresh"
    )

    new_token = Token(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        session_id=session_id,
        expiration_time=datetime.now(timezone.utc) + config.JWT_REFRESH_EXPIRY,
    )

    await new_token.save()

    return JSONResponse(
        {
            "success": True,
            "message": "User signed in successfully",
            "navigate": "/",
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
            "user": {
                "name": user.name,
                "email": user.email,
                "id": str(user.id),
            },
        },
        status_code=200,
    )


async def file_handler(credential, resume):
    credential_path = os.path.join(config.STORE_DIR, str(uuid()) + credential.filename)
    resume_path = os.path.join(config.STORE_DIR, str(uuid()) + resume.filename)

    with open(credential_path, "wb") as f:
        shutil.copyfileobj(credential.file, f)

    resume.file.seek(0)
    with open(resume_path, "wb") as f:
        shutil.copyfileobj(resume.file, f)

    return {"credential_path": credential_path, "resume_path": resume_path}


async def run_agent(credential, resume):

    files_locations = await file_handler(credential, resume)

    result = await agent_run(files_locations)

    print("Agent Result:", result)

    return JSONResponse(
        {
            "success": True,
            "message": "Agent ran successfully",
            "navigate": "/",
            "result": jsonable_encoder(result),
        },
        status_code=200,
    )
