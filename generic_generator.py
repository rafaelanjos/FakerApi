def endereco(fake):
    rua = fake.street_name()
    numero = fake.building_number() # Gera um número aleatório para o endereço
    cidade = fake.city()
    estado = fake.state_abbr() # state_abbr() para sigla, state() para nome completo
    cep = fake.postcode()
    return {
        "rua": rua,
        "numero": numero,
        "cidade": cidade,
        "estado": estado,
        "cep": cep
    }

def cartao_credito(fake, opcoes):
    raw_opcoes = None if opcoes == '' else opcoes
    cc = fake.credit_card_full(card_type=raw_opcoes).split('\n')
    return {
        "bandeira": cc[0],
        "nome": cc[1],
        "numero": cc[2].split(' ')[0],
        "validade": cc[2].split(' ')[1],
        "cvc": cc[3].split(' ')[1]
    }