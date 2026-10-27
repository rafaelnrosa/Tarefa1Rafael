import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import FreeSimpleGUI as sg

from backend import HOST, PORT, iniciar_backend

sg.theme("LightGrey1")

campos = [
    ("Nome", "nome", "-NOME-"),
    ("CPF", "cpf", "-CPF-"),
    ("RG", "rg", "-RG-"),
    ("Carteira de motorista (CNH)", "cnh", "-CNH-"),
]

layout = [
    [sg.Text("Cadastro", font=("Arial", 18, "bold"))],
    *[
        [sg.Text(rotulo, size=(30, 1)), sg.Input(key=chave_tela, size=(35, 1))]
        for rotulo, _, chave_tela in campos
    ],
    [
        sg.Button("Enviar dados", key="-ENVIAR-"),
        sg.Button("Apagar", key="-APAGAR-"),
    ],
]

servidor = iniciar_backend()
window = sg.Window("Cadastro", layout)

try:
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "-APAGAR-":
            for _, _, chave_tela in campos:
                window[chave_tela].update("")
        elif event == "-ENVIAR-":
            dados = {
                chave_api: values[chave_tela]
                for _, chave_api, chave_tela in campos
            }
            requisicao = Request(
                f"http://{HOST}:{PORT}/cadastro",
                data=json.dumps(dados).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            try:
                with urlopen(requisicao, timeout=5) as resposta:
                    retorno = json.loads(resposta.read().decode("utf-8"))
                sg.popup_ok(retorno["mensagem"], title="Cadastro")
            except HTTPError as erro:
                retorno = json.loads(erro.read().decode("utf-8"))
                sg.popup_error(retorno.get("erro", "Nao foi possivel enviar o cadastro."))
            except (URLError, TimeoutError):
                sg.popup_error("Nao foi possivel conectar ao backend local.")
finally:
    window.close()
    servidor.shutdown()
    servidor.server_close()
