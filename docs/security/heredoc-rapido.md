---
tipo: revisao-seguranca
contrato: 1
pedido: heredoc-rapido
branch: melhoria/heredoc-rapido
commit: c51715f222eb6d6b9ec0c990f5db6e5bceea4c10
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-01
---
# Review de segurança: heredoc-rapido

Etapa E1.3. Diff lido: `c454ccb..c51715f` (3 arquivos: `hooks/conformidade.py` +8/-2, `tests/test_hooks.py` +21, `changelog.d/heredoc-rapido.md` +2). Entrega o item E1 do pedido (passo 1 da proposta: `regras_do_forge` e o par raiz/home calculados uma vez por `Guarda`). Modelo de ameaças: `docs/security/ameacas/heredoc-rapido.md` (C-1 a C-6). Revisor diferente do autor.

## Gatilhos
`controles do Forge` (R-SEGURANCA): `hooks/conformidade.py` decide a recusa de escrita em caminho protegido.

## Achados
- A1 (recomendado) hooks/conformidade.py:441 · C-2 pedia `self.externo is None` fora do cache; o cache guarda o `and` inteiro. Hoje sem efeito (externo gravado em :1798 antes da decisão), mas uma chamada antes congelaria o valor. Tirar `externo` do cache.
- A2 (recomendado) tests/test_hooks.py:1824 · Casos de abuso C-5 (a) a (d) e (f) do modelo não têm teste próprio no diff; só (e) está coberto. Ficam para o QA (E1.4) escrever ou apontar a fixture existente que já os cobre.

## Detalhe dos achados
**M14 (agents/tech-lead.md:19):** 31 linhas contadas (`hooks/` 10, `tests/test_hooks.py` 21; o fragmento de changelog fica fora), abaixo de 150; um comportamento só (cache por decisão na `Guarda`), uma classe em `hooks/`. Cumpre.

**Controles do modelo:**
- C-1 cumprido: cache só em atributo da instância (`conformidade.py:373-374`), preguiçoso, sentinela `None` distinta de `False`; nada em módulo, `lru_cache` nem no `hook`. As duas `Guarda` de `principal` (`:1783` e `:1797`) são instâncias novas, então a troca de `hook.raiz` em `:1795` não herda cache. Mutante conferido (cópia em scratchpad): cache em variável de módulo derruba `test_regras_e_raiz_sao_calculadas_uma_vez_por_decisao`.
- C-2 parcial (A1): o `externo` entra no valor guardado. Caminho de ataque hoje inexistente: `Guarda.__init__` não chama `regras_do_forge`, e `externo` é gravado logo após a construção (`:1798`), antes de `decidir`; a primeira `Guarda` (`:1783`) mantém `externo=None` e é descartada. Se uma mudança futura consultar antes, o erro mais provável (`externo` None cacheado, depois um nome) só protege mais; o inverso (nome cacheado, depois None) não existe no código. Severidade baixa, informativa. Correção mínima: `return self.externo is None and self._regras`, com o cache só de `tem_manifesto_do_forge`. Esforço P. Dono: tech-lead.
- C-3 cumprido: ordem `raiz, home` e `realpath` dos dois mantidos (`:492-494`); nenhuma outra função mudou.
- C-4 cumprido: grep em `hooks/` e `bin/`: atribuições a `hook.raiz` só em `identificar_sessao` (`:1758`) e `:1795`, ambas antes da `Guarda` que decide; `externo` só em `:1798`; nenhuma escrita em `os.environ` nem `os.chdir`.
- C-5 parcial (A2): o teste novo cobre (e) e a ausência de cache entre decisões; (a) a (d) e (f) ficam com o QA (E1.4), dono qa-engineer.
- C-6 cumprido: o passo 2 (leitura da linha marcada) não está neste diff.

**Comportamento:** `python3 -m unittest tests.test_hooks` no head revisado: 61 testes, OK (152,9 s, load 2,3).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão manual do diff e grep; mutante manual numa cópia do código. `gitleaks` e `semgrep` não estão no PATH (lacuna registrada; o diff não traz credencial nem configuração).
