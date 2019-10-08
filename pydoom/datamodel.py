from typing import Any
from .fields import Field, field, _FieldInfo


__all__ = ["BaseModel"]


class MetaModel:
    def __init_subclass__(cls, openex: bool = False) -> None:
        annotations = cls.__dict__.get("__annotations__", {})
        fields = {}
        for k, v in annotations.items():
            av = getattr(cls, k, ...)
            if isinstance(av, _FieldInfo):
                finfo = av
            else:
                finfo = field(av)
            fields[k] = Field(aname=k, atype=v, ainfo=finfo)

        cls.__datamodel_fields__ = fields
        cls.__datamodel_openex__ = openex

        super().__init_subclass__()


class BaseModel(MetaModel):
    def __init__(self, **kw: Any) -> None:
        self.__datamodel_data__ = {}
        for _, fval in self.__datamodel_fields__.items():
            self.__datamodel_data__[fval.name] = fval.validate(self, kw.get(fval.alias))
        if self.__datamodel_openex__:
            self.__datamodel_data__.update(
                {
                    k: v
                    for k, v in kw.items()
                    if k not in (alias for alias in self.__datamodel_fields__)
                }
            )

    def json(self):
        return self.__datamodel_data__
