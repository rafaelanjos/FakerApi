from fastapi import FastAPI, Body
from typing import Union, Any
from datetime import datetime
import re
from pydantic import BaseModel
from faker import Faker
from renavam_generator import RenavamGenerator
from cnh_generator import CnhGenerator


class MaskOpcoes(BaseModel):
    mask: Union[bool, None] = True


class RenavamOpcoes(MaskOpcoes):
    onze: Union[bool, None] = True


class CartaoCreditoOpcoes(BaseModel):
    bandeira: Union[str, None] = None


class PlacaOpcoes(BaseModel):
    mercosul: Union[bool, None] = True


app = FastAPI()
fake = Faker('pt_BR')
fake.add_provider(RenavamGenerator)
fake.add_provider(CnhGenerator)

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
    if "sem_mask" in options or "sem-mask" in options or "nomask" in options:
        return False
    return "mask" in options or default


def _render_token(token: str) -> str:
    campo, _, raw_opcoes = token.partition(":")
    campo = campo.strip().lower()
    opcoes = _normalize_options(raw_opcoes)

    if campo == "nome":
        return fake.name()
    if campo == "endereco":
        return fake.address()
    if campo == "cpf":
        if _resolve_mask_option(opcoes):
            return fake.cpf()
        return fake.cpf().replace(".", "").replace("-", "")
    if campo == "cnpj":
        if _resolve_mask_option(opcoes):
            return fake.cnpj()
        return fake.cnpj().replace(".", "").replace("-", "").replace("/", "")
    if campo == "placa":
        mercosul = True if not opcoes else ("mercosul" in opcoes)
        if mercosul:
            return fake.bothify(text="???-#?##", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return fake.license_plate()
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

    return f"{{{{{token}}}}}"


def _render_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _render_value(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_render_value(item) for item in value]
    if isinstance(value, str):
        return FIELD_PATTERN.sub(lambda match: str(_render_token(match.group(1))), value)
    return value


@app.post("/nome")
def post_name():
    return {"resultado": fake.name()}


@app.post("/cartaocredito")
def post_cartao_credito(opcoes: CartaoCreditoOpcoes):
    """Gere dados de cartao de credito aleátorio 
        Opções de bandeira, caso não informe será gerado de forma aleatória
        Opções possiveis: 'amex', 'diners', 'discover', 'jcb', 'jcb15', 'jcb16', 'maestro', 'mastercard', 'visa', 'visa13', 'visa16', and 'visa19'
    """
    cc = fake.credit_card_full(card_type=opcoes.bandeira).split('\n')
    return {
        "bandeira": cc[0],
        "nome": cc[1],
        "numero": cc[2].split(' ')[0],
        "validade": cc[2].split(' ')[1],
        "cvc": cc[3].split(' ')[1]
    }


@app.post("/placa")
def post_placa(opcoes: PlacaOpcoes):
    if opcoes.mercosul:
        return {"resultado": fake.bothify(text='???-#?##', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')}
    else:
        return {"resultado": fake.license_plate()}


@app.post("/cpf")
def post_cpf(opcoes: MaskOpcoes):
    if opcoes.mask:
        return {"resultado": fake.cpf()}
    else:
        return {"resultado": fake.cpf().replace('.', '').replace('-', '')}


@app.post("/cnpj")
def post_cnpj(opcoes: MaskOpcoes):
    if opcoes.mask:
        return {"resultado": fake.cnpj()}
    else:
        return {"resultado": fake.cnpj().replace('.', '').replace('-', '').replace('/', '')}


@app.post("/renavam")
def post_renavam(opcoes: RenavamOpcoes):
    """Gere o código do RENAVAM(Registro Nacional de Veículos Automotores) aleatório."""

    return {"resultado": fake.renavam(opcoes.onze, opcoes.mask)}


@app.post("/cnh")
def post_cnh():
    return {"resultado": fake.cnh()}


@app.post("/dinamico")
def post_dinamico(payload: Any = Body(...)):
    return _render_value(payload)
