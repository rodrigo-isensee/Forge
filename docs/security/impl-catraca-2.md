---
tipo: revisao-seguranca
contrato: 1
pedido: impl-catraca-2
branch: melhoria/impl-catraca-2-c2
commit: 41e3d2f6fe1849962709fdddce3ef9a713df5251
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-catraca-2 (branch c2)

## Gatilhos
R-SEGURANCA, gatilho de controles do Forge: a mudança está nos testes da catraca (`tests/test_catraca.py`), que guardam o caminho do rótulo de PR mesclado. O controle em si (`tests/catraca.py`) não muda.

Item entregue: E2 do pedido (S16-TESTE-CHAVES, C2 do desenho com as correções da seção 3.2 do modelo de ameaças `docs/security/ameacas/catraca-2.md`). Diff lido: `234dbe0..41e3d2f`, commits `87e7fc6` (teste), `886b70a` (fragmento) e `41e3d2f` (parecer do review).

M14 (`agents/tech-lead.md:19`): cumpre. `git diff --numstat --no-renames 234dbe0 41e3d2f` conta 70 linhas de teste (`tests/test_catraca.py`, 69+1); o fragmento de `changelog.d/` e o parecer `.md` ficam fora. Abaixo de 150, um comportamento só (o rótulo de PR mesclado não cobre violação de chave do config), sem arquivo de `hooks/`, `.githooks/`, `bin/`, `.github/` nem de `PROTEGIDOS`.

## Achados
- A1 (recomendado) tests/test_catraca.py:2081 · a guarda de completude conta só chamadas ao nome simples `msg`; uma regra nova que emita a violação por apelido ou atributo escaparia. Hoje são 15 e batem com a tabela.
- A2 (recomendado) tests/test_catraca.py:2147 · C2-6 do modelo segue aberto: nenhum caso de chave do config na classe do squash. A guarda roda antes do squash, então não há caminho de ataque hoje; o caso custa pouco.

## Detalhe dos achados
Conferido contra o modelo de ameaças, 3.2:
- C2-1: a tabela `CHAVES_DO_CONFIG` (`tests/test_catraca.py:1858-1876`) traz as 15 formas, cada uma com o texto da regra; a de `termos_proibidos_hash` ajusta a base com uma entrada.
- C2-2: a guarda (`:2076-2084`) conta as chamadas a `msg(` em `regras_de_config` e `regra_termos_proibidos` pela árvore de sintaxe, exige igualdade com a tabela, piso de 15 e nomes sem repetição.
- C2-3: `refaz_o_pr_10_com_config` mantém no PR #10 a mudança em `tests/catraca.py` e no workflow, então a prova não é vazia.
- C2-4: refiz a mutação "filtrar o `None` de `arquivos`" no lugar da guarda (`tests/catraca.py:1017-1018`) numa cópia em `$TMPDIR`: 14 das 15 formas caem por falha de asserção (não por erro). A que segue verde é `custo_permitido novo`, porque a violação de custo é barrada antes do caminho do PR mesclado; o subteste fica como guarda desse outro controle.
- C2-5: a docstring do teste antigo passa a dizer só o que ele cobre; nenhuma asserção sai.

A1 e A2: severidade informativa, sem caminho de ataque realista hoje (quem acrescenta regra à catraca passa por review e pelo rótulo do dono, porque `tests/catraca.py` é protegido). Correção mínima de A1: na mesma guarda, falhar se `regras_de_config` ou `regra_termos_proibidos` chamarem função que não esteja numa lista fechada; de A2: um subteste de chave em `RotuloDePrSquash`. Esforço P; dono: tech-lead, numa próxima mexida.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodei `python3 -m unittest tests.test_catraca` no head revisado (263 testes, OK) e `tests.test_ambiente_git` (15, OK). `gitleaks` e `semgrep` não estão no PATH: lacuna registrada; o diff é só de teste e não traz credencial nem configuração.
