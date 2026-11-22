---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-contador-versao
commit: 1593c1a1ee1547c1c208c2293291f88fdd550a8c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E103.14, revalidação da volta de CI do CONTADOR-DA-VERSAO)

Volta única. Rodada anterior: `aprovado` em `362b45ad` (no git). Delta lido por `forge-check parecer delta`: `362b45ad..1593c1a1`; no domínio, `bin/forge-contador` (uma linha) e `skills/fluxo-do-pedido/SKILL.md` (três linhas de prosa); fora, `docs/indice-forge.md`, `tests/mutantes/v0480-contador-versao.json`, `tests/pesos-d4.json` e `tests/test_forge_contador.py`.

Gatilhos: nenhum (sem autenticação, segredo, dependência, rede, CI, banco nem controle do Forge; `bin/forge-check` intocado).

## Detalhe
Achados anteriores: nenhum.

**`bin/forge-contador:54`, `"README.md"` → `.lower() != "readme.md"`.** Pergunta da volta: a troca tira da guarda de TEXTO (`tests/test_reval_delta.py`, `Guarda`, C-2) algo que ela deveria ver? Não.
- A guarda existe para que nenhum código leia como regra um caminho que `bin/forge-check:636` (`TEXTO`) classifica como `texto` (delta que não envelhece o parecer). A linha só exclui o nome `changelog.d/README.md` de uma contagem de nomes vindos de `git ls-tree -z --name-only`; não abre nem lê conteúdo (nenhum dos marcadores de `LE_CONTEUDO`). Seria uma citação `nome`, a classe que a lista já aceita sem leitura.
- O caminho de fato tocado é `changelog.d/`, que está em `TOLERADOS` da própria guarda; e `README.md` em `TEXTO` é caminho exato (`livre`, `bin/forge-check:622-624`), ou seja, só o README da raiz, que o contador nunca toca. Um delta `texto` no README da raiz não muda a saída do contador.
- O efeito colateral é que a guarda, sensível a caixa, deixa de listar essa linha. É a mesma forma de `bin/forge-changelog:68` e `:320`, que já comparam sem caixa: contador e release concordam sobre o que é fragmento (um `changelog.d/ReadMe.md` não é contado por nenhum dos dois).
- Sonda local (repositório temporário com `changelog.d/README.md`, `ReadMe.md` e `a.md`): `forge-contador --ref HEAD` → `1.0.1: 1 de 20`, rc=0.

**Skill `fluxo-do-pedido`:** encurta a linha do contador e tira duas frases (a validação da pessoa na `main`, já dita em `agents/jarvis.md` e em `R-MAIN`, e "crie a worktree"); sem efeito de segurança; `R-MAIN` segue na fonte das regras.

Teste: `python3 -m unittest tests.test_reval_delta.Guarda tests.test_forge_contador` → 26 testes, OK. A suíte inteira fica no CI; no PR #787 o head `1593c1a1` tinha `bateria (pareceres)` e as partes 2 e 4 da suíte vermelhas na hora da leitura (o log não abriu nesta estação); a entrada na `develop` segue presa ao CI verde.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do delta, sonda local e os dois testes acima; varredor de segredos fora do PATH (lacuna, sem instalação); o delta não traz credencial.
