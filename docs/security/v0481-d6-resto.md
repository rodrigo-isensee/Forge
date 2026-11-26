---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 200d8b378582bfee881c55ef6e2574bd7f9e9ce3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 E11.25 (#877, D6 parte a: hook `salvar`, volta E11.22 por delta)

## Gatilhos
Gatilhos: hook novo fora do sandbox, controle do git (R-VERIFY core.hooksPath, R-MAIN); sem rede no hook desde o parecer anterior (opção b do dono, 25/11 07:37).

Delta lido (`forge-check parecer delta`, `50a40e28..200d8b37`): na primeira linha da branch, os commits são pareceres (`c51826d0`, `060c3ed5`, `c5ec9f94`, `a20d5389`), o merge da develop `a50975e8` (traz o #885: `bin/forge-fechar`, `docs/fechamento-integrador.md`, `tests/test_fechar.py`, specs de mutante e fragmento do changelog, com parecer próprio em `docs/security/v0481-fechar-dryrun-branch.md`, fora deste portão pela ordem do dono de 25/11) e `200d8b37`, que só cria `tests/mutantes/v0481-d6-resto-7.json`. `hooks/`, `.githooks/`, `.github/` e `scripts/` não mudam no intervalo (diff vazio). `hooks/salvar.py` está igual ao revisado em `50a40e28`.

Testes no clone em `200d8b37`:
- `bin/forge-mutante tests/mutantes/v0481-d6-resto-7.json`: M40 (`hooks/salvar.py:127`, `if e` para `if not e`) morreu e M41 (`:156`, `__main__` para `if False:`) morreu. Os dois são não equivalentes: M40 esvazia a lista a salvar e M41 desliga o hook, e `test_salva_so_o_escopo_na_copia` vê o commit sumir nos dois casos.
- `python3 -m unittest tests.test_hooks.SalvarAoParar`: 29 OK.

CI do PR no head exato: verdes `catraca` (a causa do vermelho anterior, R-QA sem mutante em `:127` e `:156`, resolvida pelo M40 e M41), as suítes 3.12 e 3.14 (partes 1 a 5), `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação`, os tetos de pulados e `árvore já provada na develop`. Vermelhos só `bateria (pareceres)`, que espera os pareceres no head novo, e `bateria`, que herda dele. Nenhum dos dois é do código.

- ci: 200d8b378582bfee881c55ef6e2574bd7f9e9ce3 verde

Estado dos achados anteriores (parecer em `50a40e28`): sem achado aberto. A4 resolvido e A5 superado ficam como estavam; o delta não toca o hook.

## O que aperta, o que é neutro e o que afrouxa
- **Aperta:** a guarda `:127` (o filtro das entradas do `git status -z`) e o ponto de entrada `:156` passam a ter mutante que morre. Um hook mudado que deixe de salvar ou de rodar agora cai na catraca.
- **Neutro:** o código do hook, o `hooks.json`, a ADR 0003 e o `R-LIMITES.md` não mudam. O que veio da develop (#885) já passou por parecer no PR de origem.
- **Afrouxa:** nada novo neste delta. O afrouxamento já declarado (commit WIP com `core.hooksPath=/dev/null`, pulando o `pre-commit` da cópia, coberto pelo `pre-push` e pelo CI) foi aprovado pelo dono em 25/11 17:37, e o PR tem o rótulo `afrouxa-regra`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `gitleaks`, Semgrep, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH (lacuna). A revisão foi manual, com o diff do intervalo, os mutantes da spec nova e a classe `SalvarAoParar` rodada localmente.
