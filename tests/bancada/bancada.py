#!/usr/bin/env python3
"""Forge: bancada de instrução (S7, 0.45.3). Compara duas versões de um texto de instrução (antes e depois) sobre casos
gravados e mede tokens e tempo por rodada. Só biblioteca padrão.

Uso: python3 tests/bancada/bancada.py --antes <arquivo> --depois <arquivo> [--casos <json>] [--rodadas N] [--executar]
- Sem `--executar` (o padrão): só valida os casos e imprime o custo estimado em tokens; não chama o modelo.
- Com `--executar`: roda `claude -p` uma vez por versão, caso e rodada, com o texto da versão como instrução extra
  (`--append-system-prompt`), sem ferramentas e sem gravar sessão, e imprime tokens e segundos por rodada e a média por versão.
Rodar com `--executar` custa tokens: só com aprovação do dono (R-CUSTO). Nada chama esta bancada sozinho, nem o CI.

Casos (`casos/*.json`): lista de objetos `{"id": "...", "entrada": "...", "espera": "..."}`; `espera` é opcional e, quando
há, é um trecho que a resposta deve conter (conta como `ok` na rodada).
Saída: 0 casos válidos (e, com --executar, todas as chamadas concluídas); 1 caso inválido ou chamada que falhou; 2 uso."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

PASTA = Path(__file__).resolve().parent
CASOS = PASTA / "casos" / "exemplo.json"
CARACTERES_POR_TOKEN = 4  # estimativa grosseira para texto em português; a medida real vem do `usage` da resposta
SAIDA_ESTIMADA = 400  # tokens de resposta por chamada, na estimativa
RODADAS_MAX = 20
TEMPO_MAX_S = 600
CAMPOS = {"id", "entrada", "espera"}


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
        if "espera" in caso and not isinstance(caso["espera"], str):
            erros.append(f"caso {n}: `espera` deve ser texto")
        if caso.get("id") in vistos:
            erros.append(f"caso {n}: id repetido {caso.get('id')}")
        vistos.add(caso.get("id"))
    return erros


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
    """Uma chamada: devolve {tokens, segundos, ok} ou None se a chamada falhou."""
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
    ok = caso["espera"] in resposta if "espera" in caso else None
    return {"tokens": tokens, "segundos": round(segundos, 1), "ok": ok}


def executar_bancada(instrucoes, casos, rodadas, executar=subprocess.run):
    """Roda tudo e imprime uma linha por rodada e a média por versão. Devolve o rc."""
    falhas = 0
    for versao, instrucao in instrucoes.items():
        medidas = []
        for caso in casos:
            for n in range(1, rodadas + 1):
                m = rodada(instrucao, caso, executar)
                if m is None:
                    falhas += 1
                    print(f"{versao} {caso['id']} rodada={n} falhou")
                    continue
                medidas.append(m)
                print(f"{versao} {caso['id']} rodada={n} tokens={m['tokens']} segundos={m['segundos']} ok={m['ok']}")
        if medidas:
            tokens = sum(m["tokens"] for m in medidas) / len(medidas)
            segundos = sum(m["segundos"] for m in medidas) / len(medidas)
            print(f"media {versao}: tokens={tokens:.0f} segundos={segundos:.1f} rodadas={len(medidas)}")
    return 1 if falhas else 0


def principal(argv=None, executar=subprocess.run):
    ap = argparse.ArgumentParser(prog="bancada", description="Compara duas versões de uma instrução sobre casos gravados.",
                                 allow_abbrev=False)
    ap.add_argument("--antes", required=True, type=Path)
    ap.add_argument("--depois", required=True, type=Path)
    ap.add_argument("--casos", type=Path, default=CASOS)
    ap.add_argument("--rodadas", type=int, default=1)
    ap.add_argument("--executar", action="store_true", help="chama o modelo (custa tokens; R-CUSTO, aprovação do dono)")
    args = ap.parse_args(argv)
    if not 1 <= args.rodadas <= RODADAS_MAX:
        ap.error(f"--rodadas deve ficar entre 1 e {RODADAS_MAX}")
    try:
        instrucoes = {"antes": args.antes.read_text(encoding="utf-8"), "depois": args.depois.read_text(encoding="utf-8")}
        casos = json.loads(args.casos.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"bancada: não consegui ler a entrada ({type(e).__name__}: {e})", file=sys.stderr)
        return 1
    erros = validar_casos(casos)
    if erros:
        for erro in erros:
            print(f"bancada: {erro}", file=sys.stderr)
        return 1
    chamadas = len(instrucoes) * len(casos) * args.rodadas
    print(f"bancada: {len(casos)} casos válidos, {chamadas} chamadas, custo estimado "
          f"{custo_estimado(instrucoes, casos, args.rodadas)} tokens")
    if not args.executar:
        print("simulação: nada foi chamado; --executar roda de verdade (custa tokens; só com aprovação do dono, R-CUSTO)")
        return 0
    return executar_bancada(instrucoes, casos, args.rodadas, executar)


if __name__ == "__main__":
    sys.exit(principal())
