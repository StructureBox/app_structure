from pydantic import BaseModel


class SteelGetSectionInput(BaseModel):
    size: str
