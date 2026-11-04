---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/tempo-b1
commit: b250b178dab0a1200945ac6bf8c120da1270a55b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: L07 da 0.33, E6 TEMPO-B1 (mensagem ao conferente só com cabeçalho, caminho e hash)

Escopo: `2c4cbf46b1e9f7f166e6504e27f13013ead1751f...b250b178dab0a1200945ac6bf8c120da1270a55b`, 1 commit (`b250b17`), 9 arquivos. Revisor de outra instância (D-ETAPAS-INST); o autor não é este revisor. Brief da implementação: `versao-033-tech-lead-41`, `## Entregar`.

Veredito: **aprovado**, sem achado bloqueante; dois recomendados (A1, A2), que não devolvem.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_mensagem_conferente tests.test_agentes_hash_brief tests.test_forge` (D-5, só os testes dos arquivos tocados): `Ran 517 tests in 138.922s` / `OK`.
- shellcheck: nenhum arquivo de shell no diff.
- `tests/config.json`: fora do diff; o invariante do conferente sobre os dois blocos segue presente (ver A2).
- Mutação no diff: responsabilidade do autor antes do push (V2); não refeita aqui.

## Conferência contra o Entregar do brief versao-033-tech-lead-41
| Item | Resultado |
|---|---|
| Worktree `melhoria/tempo-b1` sobre a develop | ok: Base-sha `2c4cbf4` é ancestral de `b250b17` |
| `bin/forge-check brief mensagem` (brief e entrega) só com o cabeçalho, sem o bloco nem os delimitadores; só imprime com o brief aprovado | ok: `bin/forge-check:5291` e `:5377` escrevem só o cabeçalho; a recusa de delimitador e de caractere de controle no texto continua antes da escrita (teste em `tests/test_forge.py:3599`); docstring do topo atualizada (`bin/forge-check:78-80`) |
| `hooks/agentes.py`: aceita a curta com `Arquivo:` em `docs/briefs/` e hash igual; recusa sem `modo:`, sem `Arquivo:`, fora de `docs/briefs/`, ausente e hash diferente; aceita a antiga; falha fechada | ok: a lógica já aceitava a curta (`hash_do_brief_diverge` lê o cabeçalho até a primeira `<<<BRIEF`, ou a mensagem inteira sem ela); o diff muda só o texto das duas recusas (`hooks/agentes.py:278`, `:282`); erro de leitura segue recusando (`:264-267`) |
| `agents/conferente.md`: nos dois modos, brief só do `Arquivo:` e hash contra `Brief-sha256:` | ok: `agents/conferente.md:37`, `:43`, `:62` e `:76`; a comparação com a cópia saiu |
| `agents/jarvis.md` e `skills/briefs-e-conferencia/SKILL.md:10` sem o texto integral; `docs/hooks.md` com a nova forma | ok: a skill foi reescrita nos dois trechos (brief e entrega); `agents/jarvis.md` não tem mais esse texto desde o L51 (`grep 'brief mensagem\|inteira'` vazio), nada a mudar; `docs/hooks.md:11` descreve as duas formas aceitas |
| Testes | ok: curta com hash certo libera nos dois modos e recusa os quatro casos (`tests/test_agentes_hash_brief.py:92-107`); a antiga segue liberando (`test_hash_do_arquivo_passa_relativo_e_absoluto`); `brief mensagem` sem o delimitador de abertura (`tests/test_forge.py:3544-3547`) e entrega sem o bloco (`tests/test_mensagem_conferente.py:48-50`) |
| Fragmento `changelog.d/tempo-b1.md` | ok: `### Alterado`, uma linha |
| Commit em Conventional Commits, push sem `-u` | ok: `feat(conferente): ...`; head remoto igual a `b250b17` |

## Compatibilidade com a mensagem antiga
O hook segue aceitando a mensagem com o bloco `<<<BRIEF` ... `BRIEF>>>` (só o cabeçalho antes do bloco conta, como antes), e o conferente é instruído a ignorar o bloco e ler o arquivo. Uma exceção: a mensagem de dois blocos (brief e entrega juntos), que o conferente ainda descreve como separada por `BRIEF>>>`, deixa de passar na forma curta. Sonda em `$TMPDIR/tech-lead-tempo-b1/sonda/` com o harness de `tests/test_agentes_hash_brief.py`: dois blocos antigos, rc 0; dois blocos curtos, rc 2 (`o cabeçalho precisa de uma só linha Arquivo: e uma só Brief-sha256:`). A recusa é de falha fechada e nenhum passo do Jarvis manda juntar os dois modos numa mensagem (`grep` em `agents/`, `skills/` e `docs/regras/`), então não é defeito de fluxo provado: vai como A2.

## Conta de linhas (decisão M14)
`git diff --numstat --no-renames 2c4cbf4...b250b17`, código e teste: `bin/forge-check` 12, `hooks/agentes.py` 4, `tests/test_agentes_hash_brief.py` 17, `tests/test_forge.py` 19, `tests/test_mensagem_conferente.py` 6; total **58**, dentro do teto de 150, sem exceção. Em `hooks/`, uma classe de comportamento só (o texto da recusa da mensagem ao conferente, `R-BRIEF`).

## `docs/regras/R-BRIEF.md`, linha 11
Ficou desatualizada: a regra ainda diz que a mensagem leva o brief integral e que o conferente compara hash e texto, o que agora contradiz `agents/conferente.md:43` e a D06 = A do pedido backlog-ate-sexta, que substitui o texto integral. O arquivo não está no Entregar do brief versao-033-tech-lead-41 (lá, o `R-BRIEF` aparece só como a descrição em `docs/hooks.md`), não é defeito de comportamento (o hook e o comando estão certos) nem segurança com gatilho: é recomendado (A1). Para entrar no L07, o Jarvis a inclui como recomendação com DECISÃO TÉCNICA no Histórico, como a DECISÃO TÉCNICA de 03:46 já prevê. A classe (texto antigo que sobra depois da mudança) é vizinha do AR-9 de `docs/engineering/achados-recorrentes.md`; a linha não foi gravada aqui porque o brief deste review limita o commit ao parecer.

## Achados
- A1 (recomendado) docs/regras/R-BRIEF.md:11 · texto da regra ainda manda a mensagem com o brief integral e a comparação do texto, contra conferente.md:43 e a D06 = A; fora do Entregar do brief 41; sugestão: atualizar no L07 como recomendação incluída
- A2 (recomendado) agents/conferente.md:16 · dois blocos ainda separados por BRIEF>>>; na forma curta o hook recusa brief e entrega juntos (sonda: rc 2, duas linhas Arquivo:); sugestão: dizer que vai um bloco por mensagem ou definir o separador novo, com o invariante

## Parecer
Aprovado. O diff cumpre os oito itens do Entregar do brief versao-033-tech-lead-41, com testes que provam a forma curta, a recusa nos quatro casos e a compatibilidade com a forma antiga. A1 (regra desatualizada) e A2 (dois blocos) são recomendados; o A2 mexe num invariante de `tests/config.json` e por isso cabe melhor em item próprio ou no E15 (BRIEF-MENSAGEM-LIMPA, L09).
