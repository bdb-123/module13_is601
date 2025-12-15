from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from uuid import UUID
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

import uvicorn

from app.auth.dependencies import get_current_active_user
from app.core.config import get_settings
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.calculation import CalculationBase, CalculationResponse, CalculationUpdate
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserLogin
from app.database import Base, get_db, engine


# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    yield

app = FastAPI(
    title="Calculations API",
    description="API for managing calculations",
    version="1.0.0",
    lifespan=lifespan
)
# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates directory
templates = Jinja2Templates(directory="templates")

# Health check endpoint for Docker health checks
@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint for Docker and CI/CD health checks.
    Returns a simple JSON response indicating the service is healthy.
    """
    return {"status": "healthy"}

# Home page route
@app.get("/", response_class=HTMLResponse, tags=["web"])
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Login page route
@app.get("/login", response_class=HTMLResponse, tags=["web"])
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Registration page route
@app.get("/register", response_class=HTMLResponse, tags=["web"])
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Dashboard page Route

@app.get("/dashboard", response_class=HTMLResponse, tags=["web"])
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# ------------------------------------------------------------------------------
# Health Endpoint
# ------------------------------------------------------------------------------
@app.get("/health", tags=["health"])
def read_health():
    return {"status": "ok"}

# ------------------------------------------------------------------------------
# User Registration Endpoint
# ------------------------------------------------------------------------------
@app.post(
    "/auth/register", 
    response_model=TokenResponse, 
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
    responses={
        201: {
            "description": "User successfully registered with JWT token",
            "model": TokenResponse
        },
        400: {
            "description": "Bad request - duplicate email/username or validation error",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already exists"}
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {"detail": "An error occurred during registration"}
                }
            }
        }
    }
)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **username**: Username (3-50 characters, must be unique)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit)
    - **confirm_password**: Optional password confirmation (must match if provided)
    
    Returns a JWT access token and refresh token upon successful registration.
    """
    try:
        # Check for duplicate email specifically (before attempting registration)
        existing_email = db.query(User).filter(User.email == user_create.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Check for duplicate username
        existing_username = db.query(User).filter(User.username == user_create.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Exclude confirm_password before passing data to User.register
        user_data = user_create.dict(exclude={"confirm_password"})
        
        # Register the user (this will hash the password and create the user)
        user = User.register(db, user_data)
        
        # Commit the transaction
        db.commit()
        db.refresh(user)
        
        # Generate JWT tokens for the newly registered user
        access_token = User.create_access_token({"sub": str(user.id)})
        refresh_token = User.create_refresh_token({"sub": str(user.id)})
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        # Return token response
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_at=expires_at,
            user_id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_verified=user.is_verified
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (duplicate email/username)
        db.rollback()
        raise
    
    except ValueError as e:
        # Handle validation errors from User.register
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        # Handle any unexpected database or system errors
        db.rollback()
        # Log the actual error for debugging (don't expose to client)
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration. Please try again later."
        )

# ------------------------------------------------------------------------------
# User Login Endpoints
# ------------------------------------------------------------------------------
@app.post(
    "/auth/login", 
    response_model=TokenResponse, 
    tags=["auth"],
    responses={
        200: {
            "description": "Login successful - JWT token returned",
            "model": TokenResponse
        },
        401: {
            "description": "Unauthorized - Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid credentials"}
                }
            }
        }
    }
)
def login_json(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return JWT tokens.
    
    - **email**: User's email address or username
    - **password**: User's password
    
    Returns access token and refresh token upon successful authentication.
    """
    try:
        # Authenticate user by email or username
        auth_result = User.authenticate(db, user_login.username, user_login.password)
        
        if auth_result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Commit the last_login update
        user = auth_result["user"]
        db.commit()

        # Ensure expires_at is timezone-aware
        expires_at = auth_result.get("expires_at")
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES
            )

        return TokenResponse(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            token_type="bearer",
            expires_at=expires_at,
            user_id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_verified=user.is_verified
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (401 Unauthorized)
        db.rollback()
        raise
    
    except Exception as e:
        # Handle any unexpected errors
        db.rollback()
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login. Please try again later."
        )

@app.post("/auth/token", tags=["auth"])
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with form data for Swagger UI"""
    auth_result = User.authenticate(db, form_data.username, form_data.password)
    if auth_result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": auth_result["access_token"],
        "token_type": "bearer"
    }

# ------------------------------------------------------------------------------
# Calculations Endpoints (BREAD)
# ------------------------------------------------------------------------------
# Create (Add) Calculation – using CalculationBase so that 'user_id' from the client is ignored.
@app.post(
    "/calculations",
    response_model=CalculationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["calculations"],
)
def create_calculation(
    calculation_data: CalculationBase,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Compute and persist a calculation.
    
    The endpoint reads the calculation type and inputs from the request (ignoring any extra fields),
    computes the result using the appropriate operation, and assigns the authenticated user's ID.
    """
    try:
        # Create the calculation using the factory method.
        new_calculation = Calculation.create(
            calculation_type=calculation_data.type,
            user_id=current_user.id,
            inputs=calculation_data.inputs,
        )
        new_calculation.result = new_calculation.get_result()

        # Persist the calculation to the database.
        db.add(new_calculation)
        db.commit()
        db.refresh(new_calculation)
        return new_calculation

    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Browse / List Calculations (for the current user)
@app.get("/calculations", response_model=List[CalculationResponse], tags=["calculations"])
def list_calculations(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    calculations = db.query(Calculation).filter(Calculation.user_id == current_user.id).all()
    return calculations

# Read / Retrieve a Specific Calculation by ID
@app.get("/calculations/{calc_id}", response_model=CalculationResponse, tags=["calculations"])
def get_calculation(
    calc_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")
    calculation = db.query(Calculation).filter(
        Calculation.id == calc_uuid,
        Calculation.user_id == current_user.id
    ).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")
    return calculation

# Edit / Update a Calculation
@app.put("/calculations/{calc_id}", response_model=CalculationResponse, tags=["calculations"])
def update_calculation(
    calc_id: str,
    calculation_update: CalculationUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")
    calculation = db.query(Calculation).filter(
        Calculation.id == calc_uuid,
        Calculation.user_id == current_user.id
    ).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")

    if calculation_update.inputs is not None:
        calculation.inputs = calculation_update.inputs
        calculation.result = calculation.get_result()
    calculation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(calculation)
    return calculation

# Delete a Calculation
@app.delete("/calculations/{calc_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["calculations"])
def delete_calculation(
    calc_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        calc_uuid = UUID(calc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid calculation id format.")
    calculation = db.query(Calculation).filter(
        Calculation.id == calc_uuid,
        Calculation.user_id == current_user.id
    ).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found.")
    db.delete(calculation)
    db.commit()
    return None

# ------------------------------------------------------------------------------
# Main Block to Run the Server
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, log_level="info")
