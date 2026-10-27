import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock, Thread


HOST = "127.0.0.1"
PORT = 8765

_cadastros = []
_cadastros_lock = Lock()

_CAMPOS_OBRIGATORIOS = ("nome", "cpf", "rg", "cnh")


class CadastroHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/cadastro":
            self._responder(404, {"erro": "Endpoint nao encontrado."})
            return

        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if tamanho <= 0 or tamanho > 16_384:
                self._responder(400, {"erro": "Tamanho da requisicao invalido."})
                return

            dados = json.loads(self.rfile.read(tamanho))
        except (ValueError, json.JSONDecodeError):
            self._responder(400, {"erro": "O corpo deve conter um JSON valido."})
            return

        if not isinstance(dados, dict) or any(
            not isinstance(dados.get(campo), str) or not dados[campo].strip()
            for campo in _CAMPOS_OBRIGATORIOS
        ):
            self._responder(400, {"erro": "Preencha todos os campos do cadastro."})
            return

        cadastro = {campo: dados[campo].strip() for campo in _CAMPOS_OBRIGATORIOS}
        with _cadastros_lock:
            _cadastros.append(cadastro)

        self._responder(201, {"mensagem": "Cadastro recebido com sucesso."})

    def _responder(self, status, conteudo):
        corpo = json.dumps(conteudo, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, format, *args):
        return


def iniciar_backend():
    servidor = ThreadingHTTPServer((HOST, PORT), CadastroHandler)
    thread = Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    return servidor
