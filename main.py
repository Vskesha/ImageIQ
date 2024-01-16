import os
import time

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.routes import users, auth, images, comments, ratings

from starlette.middleware.cors import CORSMiddleware
from src.conf.config import settings

app = FastAPI()
add_pagination(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    like connecting to databases or initializing caches.

    :return: A dictionary, which is used as the context for the app
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    await FastAPILimiter.init(r)


@app.middleware('http')
async def custom_middleware(request: Request, call_next):
    """
    The custom_middleware function is a middleware function that adds the time it took to process
    the request in seconds as a header called 'performance'

    :param request: Request: Access the request object
    :param call_next: Pass the request to the next middleware in line
    :return: A response object
    """
    start_time = time.time()
    response = await call_next(request)
    during = time.time() - start_time
    response.headers['performance'] = str(during)
    return response


app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")), name="static")
app.mount("/src", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")), name="src")


templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))
# app.mount("/docs", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)),
# "docs")), name="docs")


@app.get('/', response_class=HTMLResponse)
async def main(request: Request):
    """
    The main function is the entry point for the application.
    It will be called by Uvicorn when it starts up, and will be passed a Request object.


    :param request: Request: Get the request object that is passed to the function
    :return: A response object, which is a standard asgi response
    """
    return templates.TemplateResponse("index.html", {"request": request, "title": "WEB PROJECT"})


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks the health of the database.
    It does this by making a request to the database and checking if it returns any results.
    If there are no results, then we know something is wrong with our connection to the database.

    :param db: Session: Pass the database session to the function
    :return: A json object with a message
    """
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to project ImageIQ built on FastAPI"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )


app.include_router(users.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(images.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(ratings.router, prefix='/api')


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
