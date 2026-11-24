---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-2-delta
commit: 55a57bdef7c790c1b35971abb8c1d91a6c89c3a3
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 G1.2, revalidação por delta no head 55a57bde (E140.16)

Delta desde o parecer anterior (head 41820406): o código novo do pedido está em `bin/forge-check` (E140.12: `versoes_em_lote`, que lê as versões do parecer num `git cat-file --batch` só, e a saída antecipada de `fora_do_delta` quando o parecer não tem achado bloqueante) e em `tests/mutantes/v0480-g1-2-delta-4.json` (FD23 a FD29). O resto do intervalo vem do merge da develop. Sem suíte local; a inteira é do CI do PR.

## Mutantes (E140.12, FD23 a FD29)
`bin/forge-mutante tests/mutantes/v0480-g1-2-delta-4.json`, no head 55a57bde:

```
forge-mutante: pedido=v0480-g1-2-delta rev=55a57bdef7c7 spec=9f1e3a68c8073bbd94566961edab5a2d511a54e83116a7978e2a37c4ebda822e
FD23 · morreu · bin/forge-check:4182
FD24 · morreu · bin/forge-check:4133
FD25 · morreu · bin/forge-check:4137
FD26 · morreu · bin/forge-check:4139
FD27 · morreu · bin/forge-check:4142
FD28 · morreu · bin/forge-check:4148
FD29 · morreu · bin/forge-check:4147 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
```

Sete de sete mortos, sem sobrevivente. FD29 morreu por erro do teste sob o mutante, com o controle verde, o que a regra conta como morte. Cada linha de guarda nova do diff (o laço do lote, `missing`, o tamanho do cabeçalho, a resposta truncada, a saída antecipada) tem um mutante.

## Corpus e testes dos arquivos tocados
- Corpus: `tests.test_hooks_volta_corpus` (inclui `test_corpus_nos_dois_hooks`, que compara com `MEDIDA_DO_CORPUS`) passou. A medida em `tests/apoio_volta_unica.py` segue em 557 execuções e 4631 subprocessos, dentro do teto pedido (4631 ou menos).
- Da raiz: `python3 -m unittest tests.test_hooks_volta_corpus tests.test_parecer_fora_do_delta tests.test_testes_tocados` → `Ran 258 tests in 417.341s`, `OK (skipped=1)`. O skip é o do sandbox (`/proc` de outro namespace de pid), já existente e declarado pelo próprio teste.

## Critério → teste → resultado
A tabela de G1.2 do parecer anterior segue valendo: o delta de comportamento é só a leitura em lote (mesmo texto, menos subprocessos) e a saída antecipada sem bloqueante.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E140.12: parecer sem bloqueante não roda git | `LeiturasEmLote.test_sem_bloqueante_nao_roda_git` | sem achado bloqueante | passou; FD23 morreu |
| E140.12: lote igual ao `git show` (texto, ausente, truncado, fora do protocolo) | `LeiturasEmLote` | versão ausente, cabeçalho inválido | passou; FD24 a FD29 morreram |
| G1.2: recusa de achado fora do delta | `tests.test_parecer_fora_do_delta` | achado bloqueante fora do intervalo | passou |
| Corpus ≤ 4631 subprocessos | `test_hooks_volta_corpus` | teto de subprocessos | passou |

## Observações
Nada bloqueante. Sem bug registrado.
