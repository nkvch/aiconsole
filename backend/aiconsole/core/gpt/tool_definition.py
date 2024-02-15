from typing import Any, Literal

from pydantic import BaseModel


class ToolFunctionParameters(BaseModel):
    type: "object"
    properties: dict[str, Any]
    required: list[str]


class ToolFunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: ToolFunctionParameters


class ToolDefinition(BaseModel):
    type: Literal["function"]
    function: ToolFunctionDefinition
