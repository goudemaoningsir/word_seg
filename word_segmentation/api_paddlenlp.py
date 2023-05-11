# !/usr/bin/env python
# -*- coding:utf-8 -*-　
# @Time : 2023/5/4 22:31
# @Author : sanmaomashi
# @GitHub : https://github.com/sanmaomashi

import os
import json
import tempfile
import asyncio
import cachetools
from pydantic import BaseModel, Field, ValidationError, validator
from typing import Dict, List, Any, Literal, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form, Body, status
from fastapi.responses import JSONResponse
from paddlenlp import Taskflow
from functools import partial
from utils.common_util import cost_time, logger

SUMMARY = "中文分词"

POST_DESCRIPTION = ("分词处理API - bd\n\n\n"
                    "本API接受一个包含文本数据的对象，进行分词处理。用户可以选择上传一个自定义词典文件，覆盖预设的分词词典。\n")

DATA_DESCRIPTION = "文本分词任务的输入数据，至少包含一个文本的列表，列表中至少包含'text'字段。\n"

DICT_DESCRIPTION = ("<b>(可选)</b>自定义词典文件，将会覆盖预设的分词词典</br>\n"
                    "</br>· `accurate`模式下，词典文件每一行由一个或多个自定义item组成。词典文件user_dict.txt示例：\n"
                    "</br>---------------------------------------------------------------------------</br>"
                    "平原上的火焰</br>"
                    "上 映"
                    "</br>---------------------------------------------------------------------------</br>")


class WordSegmentation:
    def __init__(self, mode: str = "default"):
        self.model = None
        self.model_cache = cachetools.LRUCache(maxsize=10)
        self.result_cache = cachetools.LRUCache(maxsize=100)
        self.mode = mode
        self.model_future = asyncio.create_task(self.update_model(mode))

    @staticmethod
    async def load_model(mode: str, user_dict: Optional[str] = None):
        kwargs = {"user_dict": user_dict} if user_dict else {}
        return Taskflow("word_segmentation", mode=mode, **kwargs) if mode != "default" else Taskflow(
            "word_segmentation")

    async def update_model(self, mode: str, user_dict: Optional[str] = None):
        cache_key = (mode, user_dict)
        if cache_key in self.model_cache:
            self.model = self.model_cache[cache_key]
        else:
            self.model = await self.load_model(mode, user_dict)
            self.model_cache[cache_key] = self.model

    async def process_item(self, item, use_cache=False, **kwargs):
        text = item.get("text", "")
        cache_key = (text, kwargs.get('mode'), kwargs.get('user_dict'))  # 定义缓存键
        if use_cache and cache_key in self.result_cache:  # 检查是否已经在缓存中
            word_segmentation_result = self.result_cache[cache_key]
        else:
            model_callable = partial(self.model, text)
            logger.info(f"Processing item: {item}")
            word_segmentation_result = await asyncio.to_thread(model_callable)
            if use_cache:
                self.result_cache[cache_key] = word_segmentation_result  # 将结果存入缓存
            logger.info(f"Processed item: {item}, result: {word_segmentation_result}")
        return {**item, "word_segmentation_result": word_segmentation_result}


seg_router = APIRouter()


class TextData(BaseModel):
    data: List[Dict[str, Any]] = Field(..., description="需要进行分词处理的文本数据", min_items=1,
                                       error_messages={"value_error.list.min_items": "data 字段至少需要包含一个项目"})

    @validator("data", each_item=True)
    def validate_data_item(cls, item):
        if "text" not in item:
            raise ValidationError(message="data 中的每个项目都必须包含一个 'text' 键")
        return item

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    class Config:
        schema_extra = {
            "example": {
                "data": [{
                    "text": "平原上的火焰宣布延期上映"
                }, {
                    "text": "第十四届全运会在西安举办"
                }]
            }
        }


def optional_upload_file(file: Optional[UploadFile] = File(
    None,
    description=DICT_DESCRIPTION,
), ) -> Optional[UploadFile]:
    return file


word_seg = WordSegmentation("accurate")


@seg_router.post("/paddlenlp/", summary=SUMMARY, description=POST_DESCRIPTION, response_description="分词结果", )
@cost_time
async def predict(
        mode: Optional[Literal["accurate", "default"]] = Form(
            "default",
            description="分词模式，可选值为 'accurate', 'default'。默认值为 'default'",
        ),
        data: TextData = Body(..., description=DATA_DESCRIPTION),

        custom_dict: Optional[UploadFile] = Depends(optional_upload_file),
        use_cache: bool = Form(
            False,
            description="是否使用结果缓存，如果为 True，则会缓存每个项的处理结果，并在下次处理相同的项时直接返回缓存的结果。默认值为 False",
        )
):
    try:
        logger.info(f"Received request with mode: {mode}, data: {data}, custom_dict: {custom_dict}")

        await word_seg.model_future

        user_dict = None
        if custom_dict:
            with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
                f.write(custom_dict.file.read())
                user_dict = f.name

        await word_seg.update_model(word_seg.mode, user_dict)

        tasks = [asyncio.create_task(word_seg.process_item(item, use_cache=use_cache, mode=mode, user_dict=user_dict))
                 for item in data.data]
        results = await asyncio.gather(*tasks)

        if user_dict and os.path.exists(user_dict):
            os.remove(user_dict)

        response_data = {
            "task": "word_segmentation",
            "framework": "paddlenlp",
            "mode": mode,
            "user_dict": user_dict,
            "data": results
        }
        return JSONResponse(response_data)
    except Exception as e:
        logger.error(f"An error occurred during the request: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An unexpected error occurred: {e}")
