---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-adotar-vermelho
commit: 3f526e8b98a26e7e35d2b6ee5706e98dae687841
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E21.2, ADOTAR-TESTE-VERMELHO-ALHEIO)

Diff `0c47762a..3f526e8b`: 8 arquivos, 114+/8-; só texto, `tests/config.json` e um teste novo. Sem código de controle (sem guarda em `bin/`, `hooks/`, `.githooks/`): sem mutante a declarar; teto H1 não alcançado (0 linhas de código).

## Achados
- A1 (recomendado) skills/briefs-e-conferencia/teste-vermelho-alheio.md:6 · "ou cai em código que o diff não toca" abre brecha: teste verde na base e vermelho no head é do item, mesmo sem tocar o código testado (efeito indireto). Sugestão: só "cai também na base" (herdado no `--vermelho`), como a decisão diz "de outro item".
- A2 (recomendado) agents/qa-engineer.md:25 · o encurtamento trocou "indica o agente da stack que corrige" por "aponta quem corrige"; a regra fica, perde só o destino. Sem invariante tocado.

## Parecer
Aprovado (`R-REVIEW`).

- **Fidelidade à decisão do dono** (pedido v0478, Histórico 2026-11-18 13:44, "DECISÃO DO DONO 13:45"): as duas condições estão no texto. Condição 1: PR próprio e pequeno, prioridade máxima, parecer próprio do QA, nunca misturado ao PR parado, que espera só a correção e não o dono original. Condição 2: proibido apagar, pular ou afrouxar; teste errado pede a explicação do QA no parecer; mutantes do trecho seguem morrendo, sobrevivente bloqueia. Nada além do pedido; medida e critério de revisão presentes (`R-DECISAO`).
- **Invariantes:** 8 trechos novos em `tests/config.json` para o detalhe, mais o apontamento em `autor-ate-o-merge.md`; `invariantes_motivo` com regra `R-QA` e porque. O teste novo amarra cada trecho da decisão a um invariante e prova o ramo de falha (texto sem a condição 2 deixa invariante sem casar).
- **Encurtamento de `agents/qa-engineer.md`:** conferido linha a linha; as frases mudaram de forma (papel, passo 4, commit do parecer, passo 5, limites) sem regra a menos; os 8 invariantes do arquivo seguem intactos (nenhum trecho alterado está entre eles). Único estreitamento de sentido: A2.
- **`skills/qa-testing/SKILL.md`:** "vira cartão" sai para o teste que cai no HEAD; coerente com "Medida e revisão" do detalhe, que restringe a troca ao teste que para um PR.
- **Ferramentas** (sem rerrodar a suíte; ela roda no CI do PR, que esta branch ainda não tem): `python3 -I -m unittest discover -s tests -p test_teste_vermelho_alheio.py` → `Ran 5 tests ... OK`; `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_forge.Orcamento tests.test_forge.Agentes` → `Ran 11 tests ... OK` (invariantes e tamanho dos prompts); `bin/forge-testes --listar --base 0c47762a` → suíte completa (o diff toca `tests/config.json`), fica para o CI.
- Commit único em Conventional Commits, fragmento `changelog.d/v0479-adotar-vermelho.md` presente.
