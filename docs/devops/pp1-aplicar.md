# PP1: aplicar o lote do envio local (`.githooks/pre-push`)

O `.githooks/pre-push` é travado para os agentes (decisão do dono). Os consertos estão em `docs/devops/pp1-pre-push.patch`, provado por
`tests/test_pre_push_patch.py` numa cópia temporária; só o dono aplica. O patch parte do hook da `develop` e junta quatro cartões (o último em duas partes):

| Cartão | O que muda no envio local |
|---|---|
| PRE-PUSH-TEXTO-TRAVA-FD | o texto da trava vem do descritor 9 já conferido, não do caminho (link trocado depois não desvia a leitura) |
| FILA-INTERVALO-ZERO | `FORGE_FILA_INTERVALO=0` (ou `00`) é recusado como valor inválido |
| PREPUSH-LEVE-COBERTURA-CATRACA | condição mudada em Python de controle sem mutante declarado reprova no envio leve, pela mesma lista da catraca |
| PREPUSH-INDICE-E-PULOS (índice) | tocar `tests/hooks/`, `tests/config.json` ou `scripts/indice-fixtures.py` roda `scripts/indice-fixtures.py --conferir`; `docs/hooks-fixtures.md` desatualizado reprova |
| PREPUSH-INDICE-E-PULOS (pulos) | `skip`, `skipIf`, `skipUnless`, `expectedFailure` ou `skipTest` novo em `tests/` reprova (R-VERIFY; a mesma conta da catraca, sem a própria `tests/catraca.py`) |

Custo no envio leve: cerca de 0,5 s o índice e 0,7 s a contagem de pulos, só quando o diff toca esses arquivos; nenhum teste roda.

## Aplicar (o dono, na raiz do clone, na branch que traz o patch)

```bash
git apply --check docs/devops/pp1-pre-push.patch && git apply docs/devops/pp1-pre-push.patch
bash -n .githooks/pre-push && git diff --stat -- .githooks/pre-push
```

O `--check` falha sem tocar em nada se o hook em vigor já mudou (por exemplo, se o patch já foi aplicado). Depois confira o modo
executável (`ls -l .githooks/pre-push`) e commite o hook sozinho em `melhoria/*`, com o rótulo `afrouxa-regra` se a catraca pedir.

## Testar depois de aplicado

```bash
python3 -m unittest tests.test_pre_push_patch tests.test_testes_tocados
```

Com o hook já remendado, o teste confere só o remendado e pula a comparação com o original (o `git apply` do patch recusaria de novo).
