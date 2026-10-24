from fastapi import Depends, FastAPI, Response, Request
from contextlib import asynccontextmanager
from expenses.routes import router as expenses_routes
from users.routes import router as users_routes

tags_metadata = [
    {
        "name": "Expenses",
        "description": "Operations related to expense management",
        "externalDocs": {
            "description": "More about expenses",
            "url": "https://example.com/docs/expenses",
        },
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application Startup")
    yield
    print("Application Shutdown")


app = FastAPI(
    title="Expense Management Application",
    description="this is a section for description",
    version="0.0.1",
    terms_of_service="http://example.com/terms",
    contact={
        "name": "Amin Kargarzade",
        "url": "http://my_imaginary_website.com/contact/",
        "email": "aminkargarzadeh26@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

app.include_router(expenses_routes)
app.include_router(users_routes)
