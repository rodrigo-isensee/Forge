---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b2-regerar
commit: 8e4888290286ba9a46948d19583ba90e9fc90363
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-pv-b2-regerar (PR-VERDE B2, v0478 E57.53)

Revalidação por delta (`R-REVIEW`). Lido: `forge-check parecer delta` de `c5815650..8e488829`; no domínio, só `bin/forge-testes` (`SEM_BYTECODE` em `:990`, `fotografia` em `:1001-1007`, a ajuda em `:30-31`); fora do domínio, lido por alto o teste novo `Regerar.test_escrita_em_caminho_ignorado_sai_2_e_o_bytecode_nao`. A rodada anterior (head `c5815650`) fica no git.

Gatilhos: ferramenta do envio do Forge (`bin/forge-testes`), execução de geradores por subprocesso, escrita em arquivo versionado.

## Estado dos achados anteriores
- A1 (recomendado, `bin/forge-testes:1001`): corrigido. `fotografia` passou a `--ignored=traditional` com `--untracked-files=all` (arquivo a arquivo dentro da pasta ignorada) e a ajuda diz o que fica de fora (`:30-31`). Sondas S1 a S4: escrita nova ou alteração em `.forge/`, `.claude/hooks/` e `.env` aparece na diferença, logo sai 2. Teste: `test_escrita_em_caminho_ignorado_sai_2_e_o_bytecode_nao`.

## A exclusão do bytecode
O pathspec `:(exclude,glob)**/__pycache__/**` tira da fotografia tudo sob qualquer pasta `__pycache__`, na raiz ou funda (S5, S6), inclusive arquivo que não é bytecode (S7); `.pyc` fora de `__pycache__` segue visto (S8), e pasta de nome parecido não é afetada (S9). O caminho que isso abre: um gerador que grave `.pyc` envenenado em `<pasta>/__pycache__/` de um módulo importado depois por outro script. Quem escreve é o gerador ou módulo de teste medido do próprio autor, a mesma confiança da suíte (o raciocínio do A1 anterior); os arquivos de controle da sessão (`.claude/hooks`, `.claude/settings*`, `.forge/`) não ficam sob `__pycache__` e seguem vistos; a ajuda declara a exceção ("só o __pycache__ fica de fora"). Sem atacante realista e sem promessa quebrada: não é achado. Pasta vazia nova não aparece (S10), sem efeito, porque não há conteúdo a executar.

## Sondas
- S1 · `fotografia()` antes e depois de gravar `.forge/agentes.json` novo (repositório de brinquedo com o `.gitignore` da branch) · espera: `['.forge/agentes.json']` · obtido: `['.forge/agentes.json']`
- S2 · idem, alterar `.forge/agentes.json` existente · espera: o caminho · obtido: `['.forge/agentes.json']`
- S3 · idem, `.claude/hooks/h.sh` novo · espera: o caminho · obtido: `['.claude/hooks/h.sh']`
- S4 · idem, `.env` novo · espera: o caminho · obtido: `['.env']`
- S5 · idem, `scripts/__pycache__/m.cpython-312.pyc` · espera: `[]` (exceção declarada) · obtido: `[]`
- S6 · idem, `__pycache__/raiz.pyc` na raiz · espera: `[]` · obtido: `[]`
- S7 · idem, `.claude/hooks/__pycache__/h.sh` · espera: `[]` (tudo sob `__pycache__`) · obtido: `[]`
- S8 · idem, `scripts/m.pyc` fora do cache · espera: o caminho · obtido: `['scripts/m.pyc']`
- S9 · idem, `.forge/__pycache__x/a` · espera: o caminho · obtido: `['.forge/__pycache__x/a']`
- S10 · idem, pasta vazia `.forge/vazia/` · espera: `[]` · obtido: `[]`

## Riscos aceitos e ferramentas
Sem risco aceito. Suíte: não rodada aqui; a branch ainda não tem PR nem CI, e o portão de merge confere o CI verde no head. Rodei só a classe tocada: `python3 -m unittest tests.test_testes_tocados.Regerar`, 12 testes, OK. Ferramentas ausentes no PATH: varredor de segredos, SAST e linter de workflow (lacuna registrada, `R-CUSTO`); o delta não traz segredo nem workflow.
