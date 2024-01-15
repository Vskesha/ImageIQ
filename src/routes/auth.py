from fastapi import Request, Depends, HTTPException, status, APIRouter, Security, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse, Jinja2Templates

from src.conf import messages
from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.schemas.users import UserModel, UserResponse, TokenModel, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email, send_new_password, send_reset_password

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

template_directories = ['src/services/templates', 'static/client']
templates = Jinja2Templates(directory=template_directories)


@router.post("/logout")
async def logout_new_route(token: str = Depends(auth_service.token_manager.oauth2_scheme),
                           db: Session = Depends(get_db)):
    try:
        await auth_service.token_manager.logout_user(token=token, db=db)
        return "You have logged out!!!"
    except HTTPException as e:
        return e


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: Request, body: UserModel, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes a request object, body (which is the UserModel), background_tasks, and db as parameters.
        The function first checks to see if there is already an account with that email address in the database.  If so, it raises an HTTPException with status code 409 and detail &quot;Account already exists&quot;.  Otherwise it hashes the password using auth_service's password manager and then creates a new user using repository_users' create_user function.

    :param request: Request: Get the request object
    :param body: UserModel: Get the user data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background queue
    :param db: Session: Get the database session
    :return: A usermodel object
    """
    print("Request Body:", await request.body())
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.password_manager.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
        It takes the username and password from the request body,
        verifies that they are correct, and returns an access token.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Access the database
    :return: A dictionary with access_token, refresh_token and token_type
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.password_manager.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    access_token = await auth_service.token_manager.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.token_manager.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
        The refresh_token function is used to refresh the access token.
            The function takes in a refresh token and returns an access_token, a new refresh_token, and the type of token.
            If there is no user with that email or if the user's current refresh_token does not match what was passed in,
            then it will return an HTTP 401 Unauthorized error.

        :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
        :param db: Session: Get a database session
        :return: A dictionary with the new access_token, refresh_token and token type
    """
    token = credentials.credentials
    email = await auth_service.token_manager.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.token_manager.create_access_token(data={"sub": email})
    new_refresh_token = await auth_service.token_manager.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, new_refresh_token, db)
    return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
    It takes the token from the URL and uses it to get the email of the user who requested confirmation.
    The function then checks if that user exists in our database, and if not, returns an error message.
    If they do exist, we check whether their account has already been confirmed or not;
    if it has been confirmed already, we return a message saying so;
    otherwise we call our repository_users' confirmed_email function with that email as its argument.

    :param token: str: Get the email from the token
    :param db: Session: Get the database session
    :return: A message that indicates whether the email is already confirmed or not
    """
    email = auth_service.token_manager.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return RedirectResponse(url="/api/auth/email-confirm/done", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/request_email")
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that will allow them
    to confirm their account. The function takes in a RequestEmail object, which contains the email of
    the user who wants to confirm their account. It then checks if there is already an unconfirmed
    account associated with that email address, and if so it sends an email containing a confirmation link.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the request
    :param db: Session: Get a database session
    :return: A message that depends on whether the user is already confirmed or not
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        if user.confirmed:
            return JSONResponse(content={'message': messages.MSC401_EMAIL_CONFIRMED}, status_code=401)
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return JSONResponse(content={'message': messages.MSC401_EMAIL_UNKNOWN})


@router.get("/email-confirm/complate", response_class=HTMLResponse, description="Request password reset Page")
async def email_confirm_complite(request: Request) -> _TemplateResponse:
    """
    The email_confirm_complite function is used to confirm the email address of a user.
        It takes in a request object and returns an HTML template response with the title &quot;Email Confirmation Complete&quot;.
    :param request: Request: Get the request object
    :return: A message that the password has been sent to your email
    :doc-author: Trelent
    """
    return templates.TemplateResponse("email_confirm_сomplate.html", {"request": request,
                                                                      "title": messages.MSG_SENT_PASSWORD})

@router.get("/email-confirm/done", response_class=HTMLResponse, description="Request password reset Page")
async def email_confirm_done(request: Request) -> _TemplateResponse:
    r"""
    The email_confirm_done function is called when the user has successfully confirmed their email address.
    It returns a TemplateResponse object that renders the email_confirm_done.html template, which displays a message
    to the user indicating that they have successfully confirmed their email address.

    :param request: Request: Get the request object
    :return: A template response object
    :doc-author: Trelent
    """
    return templates.TemplateResponse("email_confirm_done.html", {"request": request,
                                                                  "title": messages.MSG_SENT_PASSWORD})

@router.get("/reset-password/confirm/{token}", response_class=HTMLResponse, status_code=status.HTTP_303_SEE_OTHER)
async def reset_password_confirm(token: str, background_tasks: BackgroundTasks, request: Request,
                                 db: Session = Depends(get_db)) -> dict:
    """
    The reset_password_confirm function is used to reset a user's password.
        It takes the token from the URL and uses it to get the email of the user who requested a password reset.
        The function then gets that user's information from our database, generates a new random password for them,
        hashes it using Argon2 (the same hashing algorithm we use for passwords), updates their account with this new
        hashed password, and sends an email containing their username and new temporary password.

    :param token: str: Get the email from the token
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A dictionary with the token and username
    :doc-author: Trelent
    """
    email: str = auth_service.token_manager.get_email_from_token(token)
    exist_user = await repository_users.get_user_by_email(email, db)
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=messages.MSC503_UNKNOWN_USER)

    new_password: str = auth_service.password_manager.get_new_password()
    password: str = auth_service.password_manager.get_password_hash(new_password)
    updated_user: User = await repository_users.change_password_for_user(exist_user, password, db)
    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=messages.MSC503_UNKNOWN_USER)

    background_tasks.add_task(send_new_password,
                              updated_user.email,
                              updated_user.username,
                              str(request.base_url),
                              new_password)

    response_data = {"token": token, "username": updated_user.username}
    return response_data


@router.post("/reset-password")
async def reset_password(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                         db: Session = Depends(get_db)) -> JSONResponse:
    """
    The reset_password function is used to send a password reset email to the user.
        The function takes in an email address and sends a password reset link to that address.
        If the user does not exist, it returns an error message.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A jsonresponse object
    :doc-author: Trelent
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        if user.confirmed:
            background_tasks.add_task(send_reset_password, user.email, user.username, str(request.base_url))
            return JSONResponse(content={'message': messages.MSG_SENT_PASSWORD}, status_code=200)
        return JSONResponse(content={'message': messages.EMAIL_INFO_CONFIRMED}, status_code=401)
    return JSONResponse(content={'message': messages.MSC401_EMAIL_UNKNOWN}, status_code=404)


@router.get("/reset-password/done_request", response_class=HTMLResponse, description="Request password reset Page")
async def reset_password_done(request: Request) -> _TemplateResponse:
    """
    The reset_password_done function is called when the user has successfully reset their password.
    It renders a template that informs the user that they have successfully reset their password.

    :param request: Request: Get the user's email address
    :return: A templateresponse object that renders the password_reset_done
    :doc-author: Trelent
    """
    return templates.TemplateResponse("password_reset_done.html", {"request": request,
                                                                   "title": messages.MSG_SENT_PASSWORD})
