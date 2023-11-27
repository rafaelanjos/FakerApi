from fastapi import FastAPI
from typing import Union
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
