from pydantic import BaseModel
from typing import List


class schema_folder(BaseModel):
    path: str
    title: str
    description: str


class schema_config(BaseModel):
    root: str
    target: str
    target: str
    template: str
    folders: List[schema_folder]