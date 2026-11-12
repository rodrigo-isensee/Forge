#!/usr/bin/env python3
"""Forge: bancada de instrução (S7, 0.45.3). Compara duas versões de um texto de instrução (antes e depois) sobre casos
gravados e mede tokens e tempo por rodada. Só biblioteca padrão.

Uso: python3 tests/bancada/bancada.py --antes <arquivo> --depois <arquivo> [--casos <json>] [--rodadas N]
       [--contexto <arquivo>] [--executar [--saida <json>]]
- Sem `--executar` (o padrão): só valida os casos e imprime o custo estimado em tokens; não chama o modelo.
- Com `--executar`: roda `claude -p` uma vez por versão, caso e rodada, com o texto da versão como instrução extra
  (`--append-system-prompt`), sem ferramentas e sem gravar sessão, e imprime tokens e segundos por rodada e a média por versão.
  A instrução extra leva, depois do texto da versão, a mesma nota fixa nas duas versões (`SEM_FERRAMENTAS`: não há
  ferramenta, responda só com texto) e, com `--contexto`, um contexto curto e fixo do projeto (até `CONTEXTO_MAX`
  caracteres), para o modelo não tentar inspecionar a pasta.
- `--saida ARQ` (só com `--executar`): grava em JSON, por versão, caso e rodada, a entrada, a resposta, os tokens, os
  segundos, o `ok` e o `invalida`, e o resumo por versão, para ler as respostas e comparar a qualidade.
- Rodada `invalida`: a resposta escreve uma chamada de ferramenta falsa (`<invoke`, `"name": "Bash"`) em vez de responder.
  Ela não mede nada: sai das médias e é contada à parte, por versão.
Rodar com `--executar` custa tokens: só com aprovação do dono (R-CUSTO). Nada chama esta bancada sozinho, nem o CI.

Casos (`casos/*.json`): lista de objetos `{"id": "...", "entrada": "...", "espera": "..."}`; `espera` é opcional e, quando
há, são trechos separados por `|`, e a resposta que contém algum deles conta como `ok` na rodada; a comparação ignora
maiúsculas e acentos ("Minha recomendação" conta para "recomend").
Saída: 0 casos válidos (e, com --executar, todas as chamadas concluídas); 1 caso inválido, chamada que falhou ou saída
que não se gravou; 2 uso."""
import argparse
import json
import subprocess
import sys
import re
import time
import unicodedata
from pathlib import Path

PASTA = Path(__file__).resolve().parent
CASOS = PASTA / "casos" / "exemplo.json"
CARACTERES_POR_TOKEN = 4  # estimativa grosseira para texto em português; a medida real vem do `usage` da resposta
SAIDA_ESTIMADA = 400  # tokens de resposta por chamada, na estimativa
RODADAS_MAX = 20
TEMPO_MAX_S = 600
CAMPOS = {"id", "entrada", "espera"}
CONTEXTO_MAX = 4000
SEM_FERRAMENTAS = "Você não tem ferramentas nesta conversa; responda só com texto ao usuário."
FERRAMENTA_FALSA = re.compile(r'<invoke\b|"name"\s*:\s*"Bash"')


def validar_casos(dados):
    """Erros do arquivo de casos (lista vazia = válido)."""
    if not isinstance(dados, list) or not dados:
        return ["o arquivo de casos deve ser uma lista não vazia de objetos"]
    erros, vistos = [], set()
    for n, caso in enumerate(dados, 1):
        if not isinstance(caso, dict):
            erros.append(f"caso {n}: não é objeto")
            continue
        sobra = set(caso) - CAMPOS
        if sobra:
            erros.append(f"caso {n}: campo desconhecido {', '.join(sorted(sobra))}")
        for campo in ("id", "entrada"):
            if not isinstance(caso.get(campo), str) or not caso.get(campo).strip():
                erros.append(f"caso {n}: `{campo}` ausente ou vazio")
        if "espera" in caso and not (isinstance(caso["espera"], str) and all(alternativas(caso["espera"]))):
            erros.append(f"caso {n}: `espera` deve ser texto, com alternativas não vazias separadas por |")
        if caso.get("id") in vistos:
            erros.append(f"caso {n}: id repetido {caso.get('id')}")
        vistos.add(caso.get("id"))
    return erros


def normalizado(texto):
    """Sem acento e sem diferença de maiúsculas, para comparar `espera` com a resposta."""
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)).casefold()


def alternativas(espera):
    return [normalizado(a.strip()) for a in espera.split("|")]


def atende(espera, resposta):
    """A resposta contém alguma das alternativas de `espera` (sem maiúsculas nem acentos)?"""
    texto = normalizado(resposta)
    return any(a in texto for a in alternativas(espera))


def instrucao_completa(instrucao, contexto=""):
    """O texto da versão, a nota fixa sem ferramentas e o contexto fixo do projeto, iguais nas duas versões."""
    return "\n\n".join(filter(None, [instrucao, SEM_FERRAMENTAS, contexto and f"Contexto do projeto:\n{contexto}"]))


def tokens_estimados(texto):
    return -(-len(texto) // CARACTERES_POR_TOKEN)


def custo_estimado(instrucoes, casos, rodadas):
    """Tokens estimados de toda a bancada: (instrução + entrada + resposta) por versão, caso e rodada."""
    return sum((tokens_estimados(instr) + tokens_estimados(c["entrada"]) + SAIDA_ESTIMADA) * rodadas
               for instr in instrucoes.values() for c in casos)


def comando(instrucao, entrada):
    return ["claude", "-p", entrada, "--output-format", "json", "--append-system-prompt", instrucao,
            "--tools", "", "--no-session-persistence"]


def ler_medida(saida):
    """Tokens e resposta do JSON do `claude -p --output-format json`. Devolve (tokens, resposta) ou None."""
    try:
        dados = json.loads(saida)
    except ValueError:
        return None
    if not isinstance(dados, dict) or dados.get("is_error"):
        return None
    uso = dados.get("usage") if isinstance(dados.get("usage"), dict) else {}
    tokens = sum(v for k, v in uso.items() if k.endswith("_tokens") and type(v) is int)
    return tokens, str(dados.get("result", ""))


def rodada(instrucao, caso, executar=subprocess.run):
    """Uma chamada: devolve {tokens, segundos, ok, invalida, resposta} ou None se a chamada falhou."""
    inicio = time.monotonic()
    try:
        r = executar(comando(instrucao, caso["entrada"]), capture_output=True, text=True, timeout=TEMPO_MAX_S,
                     stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        return None
    segundos = time.monotonic() - inicio
    medida = ler_medida(r.stdout) if r.returncode == 0 else None
    if medida is None:
        return None
    tokens, resposta = medida
    ok = atende(caso["espera"], resposta) if "espera" in caso else None
    return {"tokens": tokens, "segundos": round(segundos, 1), "ok": ok,
            "invalida": bool(FERRAMENTA_FALSA.search(resposta)), "resposta": resposta}


def resumir(medidas):
    """Médias das rodadas válidas, as inválidas contadas à parte e o `ok` das que têm `espera`."""
    validas = [m for m in medidas if not m["invalida"]]
    com_espera = [m for m in validas if m["ok"] is not None]
    resumo = {"rodadas": len(validas), "invalidas": len(medidas) - len(validas),
              "ok": sum(m["ok"] for m in com_espera), "com_espera": len(com_espera)}
    if validas:
        resumo["tokens"] = round(sum(m["tokens"] for m in validas) / len(validas))
        resumo["segundos"] = round(sum(m["segundos"] for m in validas) / len(validas), 1)
    return resumo


def executar_bancada(instrucoes, casos, rodadas, executar=subprocess.run, contexto=""):
    """Roda tudo e imprime uma linha por rodada e a média por versão. Devolve (rc, registro para o `--saida`)."""
    falhas, registro = 0, {"sem_ferramentas": SEM_FERRAMENTAS, "contexto": contexto, "rodadas": [], "resumo": {}}
    for versao, instrucao in instrucoes.items():
        medidas = []
        for caso in casos:
            for n in range(1, rodadas + 1):
                m = rodada(instrucao_completa(instrucao, contexto), caso, executar)
                linha = {"versao": versao, "caso": caso["id"], "rodada": n, "entrada": caso["entrada"]}
                if m is None:
                    falhas += 1
                    registro["rodadas"].append({**linha, "falhou": True})
                    print(f"{versao} {caso['id']} rodada={n} falhou")
                    continue
                medidas.append(m)
                registro["rodadas"].append({**linha, "falhou": False, **m})
                print(f"{versao} {caso['id']} rodada={n} tokens={m['tokens']} segundos={m['segundos']} ok={m['ok']}"
                      + (" invalida (chamada de ferramenta falsa)" if m["invalida"] else ""))
        resumo = registro["resumo"][versao] = resumir(medidas)
        if medidas:
            medias = f"tokens={resumo['tokens']} segundos={resumo['segundos']} " if "tokens" in resumo else ""
            print(f"media {versao}: {medias}rodadas={resumo['rodadas']} invalidas={resumo['invalidas']} "
                  f"ok={resumo['ok']}/{resumo['com_espera']}")
    return (1 if falhas else 0), registro


def gravar(saida, registro):
    """Grava o registro em JSON; devolve o rc (1 se não gravou)."""
    try:
        saida.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as e:
        print(f"bancada: não consegui gravar {saida} ({type(e).__name__}: {e})", file=sys.stderr)
        return 1
    print(f"respostas gravadas em {saida}")
    return 0


def saida_gravavel(saida):
    """Confere o destino de `--saida` antes da primeira chamada paga; devolve a mensagem do erro ou None. Não deixa arquivo novo."""
    existia = saida.exists()
    try:
        with open(saida, "a", encoding="utf-8"):
            pass
    except OSError as e:
        return f"bancada: --saida {saida} não é gravável ({type(e).__name__}: {e}); nada foi chamado"
    if not existia:
        saida.unlink(missing_ok=True)
    return None


def principal(argv=None, executar=subprocess.run):
    ap = argparse.ArgumentParser(prog="bancada", description="Compara duas versões de uma instrução sobre casos gravados.",
                                 allow_abbrev=False)
    ap.add_argument("--antes", required=True, type=Path)
    ap.add_argument("--depois", required=True, type=Path)
    ap.add_argument("--casos", type=Path, default=CASOS)
    ap.add_argument("--rodadas", type=int, default=1)
    ap.add_argument("--contexto", type=Path, help=f"contexto curto e fixo do projeto (até {CONTEXTO_MAX} caracteres)")
    ap.add_argument("--executar", action="store_true", help="chama o modelo (custa tokens; R-CUSTO, aprovação do dono)")
    ap.add_argument("--saida", type=Path, help="grava as respostas em JSON (só com --executar)")
    args = ap.parse_args(argv)
    if not 1 <= args.rodadas <= RODADAS_MAX:
        ap.error(f"--rodadas deve ficar entre 1 e {RODADAS_MAX}")
    if args.saida and not args.executar:
        ap.error("--saida só vale com --executar")
    try:
        instrucoes = {"antes": args.antes.read_text(encoding="utf-8"), "depois": args.depois.read_text(encoding="utf-8")}
        casos = json.loads(args.casos.read_text(encoding="utf-8"))
        contexto = args.contexto.read_text(encoding="utf-8").strip() if args.contexto else ""
    except (OSError, ValueError) as e:
        print(f"bancada: não consegui ler a entrada ({type(e).__name__}: {e})", file=sys.stderr)
        return 1
    if len(contexto) > CONTEXTO_MAX:
        print(f"bancada: o contexto passa de {CONTEXTO_MAX} caracteres", file=sys.stderr)
        return 1
    erros = validar_casos(casos)
    if erros:
        for erro in erros:
            print(f"bancada: {erro}", file=sys.stderr)
        return 1
    chamadas = len(instrucoes) * len(casos) * args.rodadas
    completas = {v: instrucao_completa(i, contexto) for v, i in instrucoes.items()}
    print(f"bancada: {len(casos)} casos válidos, {chamadas} chamadas, custo estimado "
          f"{custo_estimado(completas, casos, args.rodadas)} tokens")
    if not args.executar:
        print("simulação: nada foi chamado; --executar roda de verdade (custa tokens; só com aprovação do dono, R-CUSTO)")
        return 0
    if args.saida:
        erro = saida_gravavel(args.saida)
        if erro:
            print(erro, file=sys.stderr)
            return 1
    rc, registro = executar_bancada(instrucoes, casos, args.rodadas, executar, contexto)
    return max(rc, gravar(args.saida, registro)) if args.saida else rc


if __name__ == "__main__":
    sys.exit(principal())
