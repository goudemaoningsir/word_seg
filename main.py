# !/usr/bin/env python
# -*- coding:utf-8 -*-　
# @Time : 2023/5/5 20:44
# @Author : sanmaomashi
# @GitHub : https://github.com/sanmaomashi

import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html
)
from word_segmentation.api_paddlenlp import seg_router

ROOT_PATH = Path(__file__).parent

app = FastAPI(
    title="分词服务",
    openapi_url="/api/openapi.json",
    docs_url=None,
    redoc_url=None,
    default_language="zh",
    debug=True
)

app.mount("/static", StaticFiles(directory=ROOT_PATH / "static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


app.include_router(seg_router, prefix="/word_segmentation", tags=["paddlenlp"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1701, log_level="debug", reload=True)
