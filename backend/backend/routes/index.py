from fastapi import APIRouter, Request, Depends, File, UploadFile
from typing import Annotated

from backend.controller import main
from backend.validations import main as main_validator
from backend.security.jsonwebtoken import get_current_user

router = APIRouter()


@router.post("/signup")
async def signup(signup_data: main_validator.SignupValidator):
    return await main.signup(signup_data)


@router.post("/signin")
async def signin(signin_data: main_validator.SigninValidator):
    return await main.signin(signin_data)


@router.post("/run-agent")
async def run_agent(
    credential: UploadFile = File(...),
    resume: UploadFile = File(...),
    curr_user = Depends(get_current_user)
):
    return await main.run_agent(credential, resume)
