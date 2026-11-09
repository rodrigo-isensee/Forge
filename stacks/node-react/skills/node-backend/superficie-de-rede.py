#!/usr/bin/env python3
"""Varredura determinística da superfície de rede de um projeto Node/Fastify (OK-12, versao-074 E4).

Uso: python3 -I superficie-de-rede.py <raiz do projeto>

Lê `*.ts`, `*.js`, `*.mjs` e `*.cjs` em ordem alfabética, sem `node_modules/`, `dist/`, `build/` nem `.git/`, sem
seguir link simbólico e pulando arquivo acima de 1 MB (linha `pulado:`). Não executa nada do projeto, não usa rede
nem dependência: só a biblioteca padrão do Python. Uma linha por achado:

    superficie: <arquivo>:<linha> <MÉTODO> <rota> | <achado> | confirmar

e, no fim, `superficie: <N> rotas, <M> achados; reexecute: python3 -I <script> <raiz>`. Achados (lista fechada, os
itens da seção "API Node/Fastify" de `stacks/node-react/seguranca.md`):
- `sem autenticação reconhecida`: rota sem `preHandler`/`onRequest` com nome de autenticação e sem `addHook` de
  `onRequest`/`preHandler` com nome de autenticação no mesmo arquivo (o arquivo faz as vezes do plugin);
- `cors com origin aberta e credentials`: `origin: true` ou `'*'` junto de `credentials: true`;
- `rota pública sem limite de taxa reconhecido`: rota sem autenticação reconhecida, sem `rateLimit` na própria rota e
  sem `@fastify/rate-limit` global no projeto (`global: false` o desliga);
- `sem validação na borda reconhecida`: rota com corpo (POST, PUT, PATCH) sem `schema` e sem `.parse(request.body)`.

Não é portão: o `security-engineer` anexa a saída ao parecer e confirma cada linha. Toda linha pede confirmação,
e a saída nunca diz "seguro": o que a varredura não reconhece (outra forma de rota, autenticação por outro nome)
não aparece. Texto do projeto sai com caracteres de controle trocados por `?` e cortado em 200 caracteres.
Saída: 0 sempre que leu a raiz; 2 em erro de uso.
"""
import os
import re
import sys
import unicodedata
from pathlib import Path

EXTENSOES = (".ts", ".js", ".mjs", ".cjs")
PASTAS_FORA = {"node_modules", "dist", "build", ".git"}
MAXIMO_DO_ARQUIVO = 1 << 20
MAXIMO_DA_CHAMADA = 8000  # caracteres lidos depois do `(` da rota
MAXIMO_DA_LINHA = 200
METODOS = "get|post|put|patch|delete|head|options|all"
COM_CORPO = {"POST", "PUT", "PATCH"}
# Expressões sem quantificador aninhado: cada uma anda em tempo linear mesmo em código hostil.
ROTA = re.compile(rf"\.({METODOS})\(\s*(['\"`])(/[^'\"`\n]{{0,300}}|\*)\2")
ROUTE = re.compile(r"\.route\(\s*\{")
METODO_DO_ROUTE = re.compile(r"\bmethod\s*:\s*\[?\s*['\"]([A-Za-z]{1,10})['\"]")
URL_DO_ROUTE = re.compile(r"\b(?:url|path)\s*:\s*['\"`]([^'\"`\n]{0,300})['\"`]")
AUTENTICACAO = re.compile(r"auth|jwt|session|sessao|token|login|guard|protect|verifyuser|requireuser", re.I)
GANCHO_DA_ROTA = re.compile(r"\b(?:preHandler|onRequest)\s*:\s*([^\n]{0,200})")
GANCHO_DO_ARQUIVO = re.compile(r"\.addHook\(\s*['\"](?:onRequest|preHandler)['\"]\s*,\s*([^\n]{0,200})")
CORS = re.compile(r"\bcors\b\s*[,(]\s*\{", re.I)  # cors({...}) ou register(cors, {...})
ORIGEM_ABERTA = re.compile(r"\borigin\s*:\s*(?:true\b|['\"]\*['\"])")
CREDENCIAIS = re.compile(r"\bcredentials\s*:\s*true\b")
LIMITE_DA_ROTA = re.compile(r"\brateLimit\s*:")
LIMITE_GLOBAL = re.compile(r"['\"]@fastify/rate-limit['\"]|['\"]fastify-rate-limit['\"]")
LIMITE_DESLIGADO = re.compile(r"\bglobal\s*:\s*false\b")
ESQUEMA = re.compile(r"\bschema\s*:")
PARSE_DO_CORPO = re.compile(r"\.(?:safeParse|parse)\(\s*(?:req|request)\.body\b")


def limpo(texto):
    """Texto do projeto sem caractere de controle nem de formatação (ANSI, bidi) e cortado em 200 caracteres."""
    return "".join("?" if unicodedata.category(c).startswith("C") else c for c in texto)[:MAXIMO_DA_LINHA]


def arquivos(raiz):
    """(caminho relativo, caminho) dos fontes em ordem alfabética, sem as pastas de fora e sem link simbólico."""
    achados = []
    for pasta, subpastas, nomes in os.walk(raiz, followlinks=False):
        subpastas[:] = sorted(p for p in subpastas if p not in PASTAS_FORA and not os.path.islink(os.path.join(pasta, p)))
        for nome in nomes:
            caminho = os.path.join(pasta, nome)
            if nome.endswith(EXTENSOES) and not os.path.islink(caminho):
                achados.append((Path(caminho).relative_to(raiz).as_posix(), caminho))
    return sorted(achados)


def chamada(texto, inicio):
    """O texto da chamada que abre em `texto[inicio] == "("`, até o `)` que a fecha (ou o teto), pulando strings."""
    nivel, aspa, i, fim = 0, None, inicio, min(len(texto), inicio + MAXIMO_DA_CHAMADA)
    while i < fim:
        c = texto[i]
        if aspa:
            if c == "\\":
                i += 1
            elif c == aspa:
                aspa = None
        elif c in "'\"`":
            aspa = c
        elif c in "({[":
            nivel += 1
        elif c in ")}]":
            nivel -= 1
            if nivel == 0:
                return texto[inicio:i + 1]
        i += 1
    return texto[inicio:fim]


def rotas(texto):
    """(linha, MÉTODO, rota, texto da chamada) de cada rota do arquivo, na ordem em que aparecem."""
    achadas = []
    for m in ROTA.finditer(texto):
        abre = texto.index("(", m.start())
        achadas.append((m.start(), m.group(1).upper(), m.group(3), chamada(texto, abre)))
    for m in ROUTE.finditer(texto):
        corpo = chamada(texto, texto.index("(", m.start()))
        metodo, url = METODO_DO_ROUTE.search(corpo), URL_DO_ROUTE.search(corpo)
        achadas.append((m.start(), metodo.group(1).upper() if metodo else "?", url.group(1) if url else "?", corpo))
    return [(texto.count("\n", 0, ini) + 1, metodo, rota, corpo) for ini, metodo, rota, corpo in sorted(achadas)]


def autenticada(corpo, gancho_no_arquivo):
    """Autenticação reconhecida: gancho de autenticação no arquivo ou `preHandler`/`onRequest` dela na rota."""
    return gancho_no_arquivo or any(AUTENTICACAO.search(g) for g in GANCHO_DA_ROTA.findall(corpo))


def achados_da_rota(metodo, corpo, gancho_no_arquivo, limite_global):
    """Os achados de uma rota, na ordem da lista fechada."""
    achados = []
    publica = not autenticada(corpo, gancho_no_arquivo)
    if publica:
        achados.append("sem autenticação reconhecida")
    if publica and not limite_global and not LIMITE_DA_ROTA.search(corpo):
        achados.append("rota pública sem limite de taxa reconhecido")
    if metodo in COM_CORPO and not ESQUEMA.search(corpo) and not PARSE_DO_CORPO.search(corpo):
        achados.append("sem validação na borda reconhecida")
    return achados


def cors_aberto(texto):
    """Linhas das chamadas de `cors` com origem aberta junto de credenciais."""
    linhas = []
    for m in CORS.finditer(texto):
        corpo = chamada(texto, m.end() - 1)
        if ORIGEM_ABERTA.search(corpo) and CREDENCIAIS.search(corpo):
            linhas.append(texto.count("\n", 0, m.start()) + 1)
    return sorted(set(linhas))


def ler(raiz):
    """(relativo, texto) dos fontes lidos e as linhas `pulado:`."""
    lidos, pulados = [], []
    for relativo, caminho in arquivos(raiz):
        try:
            if os.path.getsize(caminho) > MAXIMO_DO_ARQUIVO:
                pulados.append(f"pulado: {limpo(relativo)} (mais de 1 MB)")
                continue
            lidos.append((relativo, Path(caminho).read_text(encoding="utf-8", errors="replace")))
        except OSError as erro:
            pulados.append(f"pulado: {limpo(relativo)} ({limpo(erro.strerror or 'erro de leitura')})")
    return lidos, pulados


def limite_global(lidos):
    """O projeto registra o limite de taxa global (`@fastify/rate-limit` sem `global: false`)?"""
    return any(LIMITE_GLOBAL.search(t) for _, t in lidos) and not any(
        LIMITE_GLOBAL.search(t) and LIMITE_DESLIGADO.search(t) for _, t in lidos)


def varrer(raiz):
    """As linhas da saída para a raiz, na ordem dos arquivos e das linhas."""
    lidos, saida = ler(raiz)
    global_ = limite_global(lidos)
    total_de_rotas = total_de_achados = 0
    for relativo, texto in lidos:
        gancho = any(AUTENTICACAO.search(g) for g in GANCHO_DO_ARQUIVO.findall(texto))
        linhas = [(n, "-", "-", "cors com origin aberta e credentials") for n in cors_aberto(texto)]
        for n, metodo, rota, corpo in rotas(texto):
            total_de_rotas += 1
            linhas += [(n, metodo, rota, a) for a in achados_da_rota(metodo, corpo, gancho, global_)]
        for n, metodo, rota, achado in sorted(linhas, key=lambda x: x[0]):
            total_de_achados += 1
            saida.append(limpo(f"superficie: {relativo}:{n} {metodo} {rota} | {achado} | confirmar"))
    saida.append(f"superficie: {total_de_rotas} rotas, {total_de_achados} achados; reexecute: python3 -I "
                 f"{limpo(str(Path(__file__).resolve()))} {limpo(str(raiz))}")
    return saida


def main(argv):
    if len(argv) != 1 or not os.path.isdir(argv[0]):
        print("uso: python3 -I superficie-de-rede.py <raiz do projeto>", file=sys.stderr)
        return 2
    print("\n".join(varrer(argv[0])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
