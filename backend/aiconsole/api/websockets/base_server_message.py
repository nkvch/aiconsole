from pydantic import BaseModel


class BaseServerMessage(BaseModel):
    def get_type(self):
        return self.__class__.__name__

    def model_dump(self, **kwargs):
        # Don't include None values, call to super to avoid recursion
        return {k: v for k, v in super().model_dump(**kwargs).items() if v is not None}
