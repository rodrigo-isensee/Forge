---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-contador-versao
commit: 3a4fd5c0582c5b0700a67fa04eb6a8877093c058
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E103.19, revalidação do CONTADOR-DA-VERSAO)

Volta única. Rodada anterior: `aprovado` em `1593c1a1` (no git). Delta lido por `forge-check parecer delta`: `1593c1a1..3a4fd5c0`, sem o que veio da `develop`; no domínio, só `skills/fluxo-do-pedido/SKILL.md`; fora, `tests/mutantes/v0480-contador-versao-5.json`, `tests/test_forge_contador.py` e `tests/test_reval_delta.py`. `bin/forge-contador` e `bin/forge-check` intocados no delta.

Gatilhos: nenhum (sem autenticação, segredo, dependência, rede, CI, banco nem controle do Forge alterado).

## Detalhe
Achados anteriores: nenhum.

**Skill `fluxo-do-pedido`:** `git diff origin/develop HEAD -- skills/` vazio; a skill volta ao texto da `develop` (repõe "A pessoa valida e faz o merge na `main`" e "crie a worktree", tira a linha do contador). Sem efeito de segurança; `R-MAIN` volta a ser dito também na skill.

**`tests/test_reval_delta.py` (fora do domínio, lido por tocar a guarda de TEXTO):** a única mudança é `"tests/test_forge_contador.py": 2` em `_NOME`, classe `nome`. As duas citações (`tests/test_forge_contador.py:90` e `:117`) são nomes de arquivo sintéticos gravados num repositório temporário do teste; não leem conteúdo de `README.md` como regra. Confirma o que já disse em `1593c1a1`: a entrada não esconde leitura de conteúdo.

**`tests/test_forge_contador.py`:** volta a `changelog.d/README.md` e acrescenta `Readme.md` (caixa mista não conta), fechando o mutante do `.lower()` em `bin/forge-contador:54`.

Teste: `python3 -m unittest tests.test_reval_delta.Guarda tests.test_forge_contador` → 27 testes, OK. Suíte inteira no CI do PR #787: as partes da suíte em 3.12 e 3.14 lidas verdes; `bateria (pareceres)` vermelha na leitura, por pareceres presos ao head anterior (este grava o novo). A entrada na `develop` segue presa ao CI verde.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do delta e os testes acima; varredor de segredos fora do PATH (lacuna, sem instalação); o delta não traz credencial.
