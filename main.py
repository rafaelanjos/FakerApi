from fastapi import FastAPI, Body
from typing import Union, Any
from pydantic import BaseModel
from faker import Faker
from renavam_generator import RenavamGenerator
from cnh_generator import CnhGenerator
from dinamic_generator import dinamico
import generic_generator


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
    return generic_generator.cartao_credito(fake, opcoes.bandeira)


@app.post("/placa")
def post_placa(opcoes: PlacaOpcoes):
    if opcoes.mercosul:
        return {"resultado": fake.bothify(text='???-#?##', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')}
    else:
        return {"resultado": fake.license_plate()}


@app.post("/cpf")
def post_cpf(opcoes: MaskOpcoes):
    return {"resultado": fake.cpf() if opcoes.mask else fake.cpf().replace('.', '').replace('-', '')}


@app.post("/cnpj")
def post_cnpj(opcoes: MaskOpcoes):
    return {"resultado": fake.cnpj() if opcoes.mask else fake.cnpj().replace('.', '').replace('-', '').replace('/', '')}


@app.post("/renavam")
def post_renavam(opcoes: RenavamOpcoes):
    """Gere o código do RENAVAM(Registro Nacional de Veículos Automotores) aleatório."""
    return {"resultado": fake.renavam(opcoes.onze, opcoes.mask)}


@app.post("/cnh")
def post_cnh():
    return {"resultado": fake.cnh()}


@app.post("/dinamico")
def post_dinamico(payload: Any = Body(...)):
    return dinamico(fake, payload)


@app.post("/endereco")
def post_name():
    return {"resultado": generic_generator.endereco(fake)}