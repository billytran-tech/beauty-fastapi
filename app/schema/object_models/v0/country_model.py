from pydantic import BaseModel


class Currency(BaseModel):
    code: str
    symbol: str
    name: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Country(BaseModel):
    name: str
    code: str
    currency: Currency

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
