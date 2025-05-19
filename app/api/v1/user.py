from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.schemas.user import UserResponse, UserUpdate, UserPreferences
from app.models.user import User as UserModel
from app.utils.auth import get_password_hash

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
def get_user_profile(current_user: UserModel = Depends(get_current_user)):
    """
    Get the current user's complete profile including preferences
    """
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile information
    """
    if user_update.username is not None:
        current_user.username = user_update.username
    if user_update.password is not None:
        current_user.password = get_password_hash(user_update.password)
    if user_update.travel_style is not None:
        current_user.travel_style = user_update.travel_style
    if user_update.budget_range is not None:
        current_user.budget_range = user_update.budget_range

    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/preferences", response_model=UserResponse)
def update_user_preferences(
    preferences: UserPreferences,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user travel preferences
    """
    if preferences.travel_style is not None:
        current_user.travel_style = preferences.travel_style
    if preferences.budget_range is not None:
        current_user.budget_range = preferences.budget_range
    if preferences.destination:
        current_user.preferred_destinations = ",".join(preferences.destination)

    db.commit()
    db.refresh(current_user)
    return current_user