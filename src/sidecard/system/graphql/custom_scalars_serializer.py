from ariadne import ScalarType

__all__: list[str] = ["integer_scalar", "float_scalar"]

integer_scalar: ScalarType = ScalarType("Integer")
float_scalar: ScalarType = ScalarType("Float")


@integer_scalar.serializer
def serialize_integer(value: int):
    return int(value)


@float_scalar.serializer
def serialize_float(value: float):
    return float(value)
