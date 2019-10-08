""" Field class """
import re
from typing import Any, Callable, Union


class _FieldInfo:
    __slots__ = (
        "default",
        "alias",
        "title",
        "description",
        "const",
        "gt",
        "gte",
        "lt",
        "lte",
        "multi",
        "min_len",
        "max_len",
        "regex",
        "validator",
    )

    def __init__(
        self,
        default: Any,
        *,
        alias: str = None,
        title: str = None,
        description: str = None,
        const: bool = False,
        gt: Any = None,
        gte: Any = None,
        lt: Any = None,
        lte: Any = None,
        multi: float = None,
        min_len: int = None,
        max_len: int = None,
        regex: str = None,
        validator: Union[Callable[[Any], bool], str],
    ) -> None:
        self.default = default
        self.alias = alias
        self.title = title
        self.description = description
        self.const = const
        self.gt = gt
        self.gte = gte
        self.lt = lt
        self.lte = lte
        self.multi = multi
        self.min_len = min_len
        self.max_len = max_len
        self.regex = regex
        self.validator = validator

    def __repr__(self) -> str:
        attrs = ((s, getattr(self, s)) for s in self.__slots__)
        return "FieldInfo({})".format(", ".join(f"{a}:{v!r}" for a, v in attrs))


class Field:
    def __init__(self, aname: str, atype: type, ainfo: _FieldInfo) -> None:
        self.name = aname
        self.type = atype
        self.alias = ainfo.alias
        self.default = ainfo.default
        self.required = False
        self.title = ainfo.title
        self.description = ainfo.description
        self.const = ainfo.const
        self.gt = ainfo.gt
        self.gte = ainfo.gte
        self.lt = ainfo.lt
        self.lte = ainfo.lte
        self.multi = float(ainfo.multi) if ainfo.multi is not None else None
        self.min_len = int(ainfo.min_len) if ainfo.min_len is not None else None
        self.max_len = int(ainfo.max_len) if ainfo.max_len is not None else None
        self.regex = ainfo.regex
        self.validator = ainfo.validator

        if not self.alias:
            self.alias = self.name

        if self.default == ...:
            self.required = True

        if (
            not self.required
            and self.default is not None
            and not isinstance(self.default, self.type)
        ):
            raise TypeError("type of the ``default`` value is invalid.")

        if self.required and self.const:
            raise ValueError("``default`` value can not be empty.")

        for fd in (self.gt, self.gte, self.lt, self.lte):
            if fd is not None and not isinstance(fd, self.type):
                raise TypeError(f"type of the ``{fd.__name__}`` value is invalid.")

        if not self.validator:
            self.validator = self.valid_all

    def valid_gt(self, val: Any) -> bool:
        if val > self.gt:
            return True
        return False

    def valid_gte(self, val: Any) -> bool:
        if val >= self.gte:
            return True
        return False

    def valid_lt(self, val: Any) -> bool:
        if val < self.lt:
            return True

        return False

    def valid_lte(self, val: Any) -> bool:
        if val <= self.lte:
            return True

        return False

    def valid_multi(self, val: Any) -> bool:
        mod = val / self.multi % 1
        if almost_equal_floats(mod, 0.0) or almost_equal_floats(mod, 1.0):
            return True

        return False

    def valid_minlen(self, val: Any) -> bool:
        if len(Any) >= self.min_len:
            return True

        return False

    def valid_maxlen(self, val: Any) -> bool:
        if len(val) <= self.max_len:
            return True

        return False

    def valid_regex(self, val: Any) -> bool:
        if re.fullmatch(self.regex, val):
            return True

        return False

    def valid_all(self, val: Any) -> bool:
        brst = True
        if self.gt is not None:
            brst &= self.valid_gt(val)

        if brst and self.gte is not None:
            brst &= self.valid_gte(val)

        if brst and self.lt is not None:
            brst &= self.valid_lt(val)

        if brst and self.lte is not None:
            brst &= self.valid_lte(val)

        if brst and self.multi is not None:
            brst &= self.valid_multi(val)

        if brst and self.min_len is not None:
            brst &= self.valid_minlen(val)

        if brst and self.max_len is not None:
            brst &= self.valid_maxlen(val)

        if brst and self.regex is not None:
            brst &= self.valid_regex(val)

        return brst

    def validate(self, cls: object, val: Any = ...) -> Any:
        """ Verify the validity of the field data provided.

        When ``val`` equals to ``...``, means the fields data
        was not provided.

        We checking for the default value only when the field
        data was not provided."""
        use_default = False
        if self.const:
            val = self.default
            use_default = True

        if val == ...:
            if self.required:
                raise ValueError(f"``{self.alias}`` was required.")
            val = self.default
            use_default = True

        # For now, we are not considering scenarios where the
        # field annotation type are custom class or ``typing``
        # types.
        val = self.type(val)

        # Custom validator was provided, ``self.validator``
        # value will be the cls's classmethod name.
        if isinstance(self.validator, str):
            cmtd = getattr(cls, self.validator, None)
            if not cmtd:
                raise ValueError("validator ``self.validator`` not find.")

            self.validator = cmtd

        if not self.validator(val):
            if use_default:
                raise ValueError(f"``{self.alias}`` default value incorrect.")

            raise ValueError(f"``{self.alias}`` received value incorrect.")

        return val


def field(
    default: Any,
    *,
    alias: str = None,
    title: str = None,
    description: str = None,
    const: bool = False,
    gt: Any = None,
    gte: Any = None,
    lt: Any = None,
    lte: Any = None,
    multi: float = None,
    min_len: int = None,
    max_len: int = None,
    regex: str = None,
    validator: Union[Callable[[Any], bool]] = None,
) -> Any:
    """ Used to descript a field with more detailed infomation.

    default: The field default value, use (``...``) to indicate the field is
    required.

    alias: The checking name of the field.

    title: Used in schema.

    decription: Used in schema.

    const: If true, this field will be const field, it's value will always
    be the default value.

    gt/gte/lt/lte: Comparetions. The schema will have a ``exclusiveMinimun/
    minimum/exclusiveMaximum/maximum`` validation keyword.

    multi: Requires the comming value must be "a multiple of" the default
    value. The schema will have a ``multipleOf`` validation keyword.

    min_len/max_len: Requires the field to have a minimum/maximum length.
    The schema will have a ``minLength/maxLength`` validation keyword.

    regex: Only applies to strings, regular expression match. The schema will
    have a ``pattern`` validation keyword.

    validator: a classmethod name for custome validator, if this field
    was not provided, we will generate a validator (type is Callable)
    with the basic constraints above mentioned.
    """
    return _FieldInfo(
        default,
        alias=alias,
        title=title,
        description=description,
        const=const,
        gt=gt,
        gte=gte,
        lt=lt,
        lte=lte,
        multi=multi,
        min_len=min_len,
        max_len=max_len,
        regex=regex,
        validator=validator,
    )


def almost_equal_floats(value_1: float, value_2: float, *, delta: float = 1e-8) -> bool:
    """ Return True if two are almost equal. """
    return abs(value_1 - value_2) <= delta
