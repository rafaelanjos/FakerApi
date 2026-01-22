from fastapi import FastAPI, Body
from typing import Union, Any
from datetime import datetime
import re
from pydantic import BaseModel
from faker import Faker
import generic_generator

FIELD_PATTERN = re.compile(r"\{\{([^{}]+)\}\}")


def _format_standard_datetime(value: datetime, specifier: str) -> str:
    if specifier == "d":
        return f"{value.month}/{value.day}/{value.year}"
    if specifier == "D":
        return f"{value.strftime('%A')}, {value.strftime('%B')} {value.day:02}, {value.year}"
    if specifier == "t":
        return value.strftime("%I:%M %p").lstrip("0")
    if specifier == "T":
        return value.strftime("%I:%M:%S %p").lstrip("0")
    if specifier == "f":
        return f"{_format_standard_datetime(value, 'D')} {_format_standard_datetime(value, 't')}"
    if specifier == "F":
        return f"{_format_standard_datetime(value, 'D')} {_format_standard_datetime(value, 'T')}"
    if specifier == "g":
        return f"{_format_standard_datetime(value, 'd')} {_format_standard_datetime(value, 't')}"
    if specifier == "G":
        return f"{_format_standard_datetime(value, 'd')} {_format_standard_datetime(value, 'T')}"
    if specifier == "M":
        return value.strftime("%d-%b")
    if specifier == "r":
        return value.strftime("%a, %d %b %Y %H:%M:%S GMT")
    if specifier == "s":
        return value.strftime("%Y-%m-%dT%H:%M:%S")
    if specifier == "u":
        return value.strftime("%Y-%m-%d %H:%M:%SZ")
    if specifier == "Y":
        return value.strftime("%B, %Y")
    return value.isoformat()


def _format_datetime(value: datetime, fmt: str) -> str:
    if len(fmt) == 1:
        return _format_standard_datetime(value, fmt)

    tokens = [
        ("yyyy", lambda v: f"{v.year:04}"),
        ("yy", lambda v: f"{v.year % 100:02}"),
        ("MMMM", lambda v: v.strftime("%B")),
        ("MMM", lambda v: v.strftime("%b")),
        ("MM", lambda v: f"{v.month:02}"),
        ("M", lambda v: str(v.month)),
        ("dddd", lambda v: v.strftime("%A")),
        ("ddd", lambda v: v.strftime("%a")),
        ("dd", lambda v: f"{v.day:02}"),
        ("d", lambda v: str(v.day)),
        ("HH", lambda v: f"{v.hour:02}"),
        ("hh", lambda v: f"{(v.hour % 12) or 12:02}"),
        ("mm", lambda v: f"{v.minute:02}"),
        ("ss", lambda v: f"{v.second:02}"),
        ("fff", lambda v: f"{int(v.microsecond / 1000):03}"),
        ("FFF", lambda v: f"{int(v.microsecond / 1000):03}".rstrip("0")),
        ("tt", lambda v: v.strftime("%p")),
    ]

    result = []
    i = 0
    while i < len(fmt):
        matched = False
        for token, formatter in tokens:
            if fmt.startswith(token, i):
                result.append(formatter(value))
                i += len(token)
                matched = True
                break
        if not matched:
            result.append(fmt[i])
            i += 1
    return "".join(result)


def _normalize_options(raw: str) -> set:
    if not raw:
        return set()
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


def _resolve_mask_option(options: set, default: bool = False) -> bool:
    if not options:
        return default
    return "mask" in options or default


def _render_token(fake, token: str) -> Any:
    campo, _, raw_opcoes = token.partition(":")
    campo = campo.strip().lower()
    opcoes = _normalize_options(raw_opcoes)

    if campo == "nome":
        return fake.name()
    if campo == "endereco":
        return generic_generator.endereco(fake)
    if campo == "cpf":
        return fake.cpf() if _resolve_mask_option(opcoes) else fake.cpf().replace(".", "").replace("-", "")
    if campo == "cnpj":
        return fake.cnpj() if _resolve_mask_option(opcoes) else fake.cnpj().replace(".", "").replace("-", "").replace("/", "")
    if campo == "placa":
        mercosul = True if not opcoes else ("mercosul" in opcoes)
        return fake.bothify(text="???-#?##", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ") if mercosul else fake.license_plate()
    if campo == "renavam":
        onze = "onze" in opcoes
        mask = _resolve_mask_option(opcoes)
        return fake.renavam(onze, mask)
    if campo == "cnh":
        return fake.cnh()
    if campo == "hoje":
        if raw_opcoes:
            return _format_datetime(datetime.now(), raw_opcoes)
        return datetime.now().isoformat()
    if campo == "cartaocredito":
        return generic_generator.cartao_credito(fake, raw_opcoes)
    return f"{{{{{token}}}}}"


def _render_value(fake, value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _render_value(fake, val) for key, val in value.items()}
    if isinstance(value, list):
        return [_render_value(fake, item) for item in value]
    if isinstance(value, str):
        exact_match = FIELD_PATTERN.fullmatch(value)
        if exact_match:
            return _render_value(fake, _render_token(fake, exact_match.group(1)))
        return FIELD_PATTERN.sub(lambda match: str(_render_token(fake, match.group(1))), value)
    return value


def dinamico(fake, payload) -> str:
    return _render_value(fake, payload)