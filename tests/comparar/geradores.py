"""AE7.2 (v0478 E107.1): as famílias geradas do `forge-check comparar`, somadas ao `tests/comparar/corpus.jsonl`.

Cada família é um comando proibido (o núcleo) vestido por invólucros de shell que o hook precisa ver através (prefixo de
ambiente, `env`, `command`, encadeamento, subshell, `sh -c`); o sorteio escolhe `POR_FAMILIA` combinações com
`random.Random(semente)`, então a mesma semente dá sempre os mesmos casos. O comparador roda este arquivo de cada lado (base
e head) com `python3 -I - <semente>` e lê um caso JSON por linha, no formato do corpus; a semente é a dele, fixa e impressa
na saída (`familias: semente=<n> ...`). Só biblioteca padrão; nada lê o ambiente, o disco nem a hora."""
import itertools
import json
import random
import sys

POR_FAMILIA = 8
NUCLEOS = {
    "merge-pr": ("gh pr merge 12", "gh pr merge 12 --squash", "gh pr merge --admin 12", "gh  pr  merge 12"),
    "push-forcado": ("git push --force origin main", "git push -f origin develop", "git push origin +main",
                     "git push --force-with-lease origin homolog"),
    "sem-verificar": ("git commit --no-verify -m x", "git commit -n -m x", "git push --no-verify origin melhoria/x",
                      "git commit -qnm x"),
}
INVOLUCROS = ("{}", "env {}", "command {}", "X=1 {}", "true && {}", "true; {}", "( {} )", "sh -c '{}'", "bash -c \"{}\"",
              "{} 2>/dev/null")


def familias(semente):
    """{família: [caso]} da `semente`, cada caso no formato do corpus, com o id `gerada/<família>/<n>`."""
    sorteio = random.Random(semente)
    saida = {}
    for nome, nucleos in sorted(NUCLEOS.items()):
        pares = sorteio.sample(list(itertools.product(nucleos, INVOLUCROS)), POR_FAMILIA)
        saida[nome] = [{"id": f"gerada/{nome}/{n:02d}", "arquivos": {"src/app.js": "v1\n"},
                        "entrada": {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_use_id": "toolu_9",
                                    "tool_input": {"command": involucro.format(nucleo)}}}
                       for n, (nucleo, involucro) in enumerate(pares, 1)]
    return saida


if __name__ == "__main__":
    for casos in familias(int(sys.argv[1])).values():
        for caso in casos:
            print(json.dumps(caso, sort_keys=True, ensure_ascii=False))
