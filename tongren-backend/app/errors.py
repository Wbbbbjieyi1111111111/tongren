"""
统一响应体 / 业务异常

契约（docs/API-CONTRACT.md 1.1）：
  成功 { code: 0, message: "ok", data: ... }
  失败 { code: 40001|40101|40401|50001, message: "...", data: null }

小程序端 common/api.js 只认响应体里的 code，因此业务错误统一以 HTTP 200
返回错误码体，保证前端 toast 能展示后端 message。
"""
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

CODE_OK = 0
CODE_PARAM = 40001       # 参数错误
CODE_UNAUTH = 40101      # 未登录 / token 失效
CODE_NOT_FOUND = 40401   # 资源不存在
CODE_SERVER = 50001      # 服务器内部错误


class ApiError(Exception):
    """业务异常，抛出后由全局异常处理器包装成统一响应体"""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def ok(data: Any = None) -> dict:
    return {"code": CODE_OK, "message": "ok", "data": data}


def fail(code: int, message: str) -> dict:
    return {"code": code, "message": message, "data": None}


def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(status_code=200, content=fail(exc.code, exc.message))


def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    first = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(x) for x in first.get("loc", []) if x != "body") or "参数"
    return JSONResponse(
        status_code=200,
        content=fail(CODE_PARAM, f"参数错误：{field} {first.get('msg', '')}"),
    )


def server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=200, content=fail(CODE_SERVER, "服务器内部错误"))
