# !/usr/bin/env python
# -*- coding:utf-8 -*-　
# @Time : 2023/5/5 10:11 
# @Author : sanmaomashi
# @GitHub : https://github.com/sanmaomashi

import os
import time
import json

from asyncio.coroutines import iscoroutinefunction
from functools import wraps
from fastapi.responses import JSONResponse
import sys
from loguru import logger
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOGURU_PATH = os.path.join(BASE_DIR, "log", "models.log")


def cost_time(func):
    """ 获取函数执行时间 """
    @wraps(func)
    async def func_async(*args, **kwargs):
        t = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed_time = time.perf_counter() - t
        if isinstance(result, JSONResponse):
            result_content = result.body.decode()
            result_dict = json.loads(result_content)
            result_dict["speed_time"] = elapsed_time
            return JSONResponse(result_dict)
        return result

    if iscoroutinefunction(func):
        return func_async
    else:
        return func


class Logger:
    def __init__(self, log_file_path=LOGURU_PATH):
        print(LOGURU_PATH)
        self.logger = logger
        # 清空所有设置
        self.logger.remove()
        # 添加控制台输出的格式,sys.stdout为输出到屏幕;关于这些配置还需要自定义请移步官网查看相关参数说明
        self.logger.add(sys.stdout,
                        format=
                               "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "  # 颜色>时间
                               "<level>{level}</level> | "  # 等级
                               # "{process.name} | "  # 进程名
                               # "{thread.name} | "  # 进程名
                               "<cyan>{module}</cyan>.<cyan>{function}</cyan>"  # 模块名.方法名
                               ":<cyan>{line}</cyan> | "  # 行号
                               "<level>{message}</level>",  # 日志内容
                        enqueue=True)
        # 输出到文件的格式,注释下面的add',则关闭日志写入
        self.logger.add(log_file_path, level='DEBUG',
                        format='{time:YYYY-MM-DD HH:mm:ss} - '  # 时间
                               # "{process.name} | "  # 进程名
                               # "{thread.name} | "  # 进程名
                               '{module}.{function}:{line} - {level} -{message}',  # 模块名.方法名:行号
                        rotation="10 MB", enqueue=True)

    def get_logger(self):
        return self.logger


logger = Logger().get_logger()


if __name__ == '__main__':
    logger.info(2222222)
    logger.debug(2222222)
    logger.warning(2222222)
    logger.error(2222222)
    logger.exception(2222222)
