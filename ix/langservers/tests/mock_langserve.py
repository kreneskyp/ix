#!/usr/bin/env python

from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langserve import add_routes


app = FastAPI(
    title="PirateServe",
    version="1.0",
    description="A simple api for pirate jokes",
)

model = ChatOpenAI()

prompt = ChatPromptTemplate.from_template(
    "tell me a joke about {topic}, but talk like a pirate when you deliver it"
)
add_routes(
    app,
    prompt | model,
    path="/jokes",
)

prompt = ChatPromptTemplate.from_template(
    "tell me a sea tale about {topic}, but talk like a pirate when you deliver it"
)
add_routes(
    app,
    prompt | model,
    path="/tales",
)

mock_openapi_schema = get_openapi(
    title="PirateServe",
    version="1.0",
    description="A simple api for pirate jokes",
    routes=app.routes,
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=9000)
