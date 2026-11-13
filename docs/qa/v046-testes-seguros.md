---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/testes-seguros
commit: 8fc857c94212789ba54f2db909cd09bb9325525f
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-11
---
# Parecer de QA - v046 E2.2 testes seguros (head 8fc857c9)

Diff conferido (`origin/develop...ebdde388`): `tests/test_forge.py`, `tests/test_pedido_fora.py`, fragmento de changelog. Sem código de produção. Leitura da branch sem escrever nela (Z10); extração do head com `git archive` em `$TMPDIR`.

## Achados

## Critério → teste → resultado
| Critério (E2.2) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| TESTE-REDE-ANTHROPIC: nenhum teste tenta rede para API paga (R-CUSTO) | `PrepararEstacao` (`--simular`): `claude` falso no PATH; afirma `claude_log == ["plugin list"]` e a linha `[simular] claude plugin install forge@forge --scope user` | CLI real nunca é chamada; a única chamada é `plugin list` | passou (11 testes OK) |
| TESTE-FORA-DO-CLONE: nenhum teste lê arquivo fora do clone | `test_pedido_fora`, subteste `../../x.md`: `cwd` em `tmp/c1/c2/c3` (onde o caminho não existe) e alvo plantado em `tmp/x.md`; afirma rc 2 e nenhuma linha `origem:` nem `conferencia-brief-regra:` | recusa vem só da regra de raízes, não do acaso do disco | passou (20 testes OK) |

## Cenários e resultado real
- `python3 -m unittest tests.test_pedido_fora`: Ran 20, OK (34 s).
- `python3 -m unittest tests.test_forge.PrepararEstacao`: Ran 11, OK (2,5 s).
- Leitura: `rodar_em` espelha `rodar` (mesmo HOME, `--raiz`, SCRIPT_DIRETO), só troca o `cwd`. O falso `claude` sai 1 e registra os argumentos em log próprio, fora do `registro` de comandos que alteram o sistema, então a asserção `assertFalse(registro.exists())` segue válida.
- Vermelho antes do verde e mutação: não se aplicam (robustez de teste existente, sem regra nova nem código de produção). Suíte inteira: decide o check-run `bateria` do PR neste sha; não rerrodada aqui.

## Bug
Nenhum.

## Revalidação (volta 1, delta ebdde388..8fc857c9)
Delta lido: `tests/test_forge.py` (NVM_DIR fixado em `home/.nvm` nos dois ambientes de `preparar-estacao`; sentinela `nvm.sh` alheio com `mock.patch.dict` prova que o ambiente do teste está contaminado e afirma `marca` inexistente; `dpkg-query` falso), `tests/test_pedido_fora.py` (comentário corrigido; afirma `brief: não consegui ler` no caso `../../x.md`), fragmento de changelog. Sem código de produção; nenhum achado aberto antes nem agora.
- `NVM_DIR=/nonexistent python3 -m unittest tests.test_forge.PrepararEstacao` (extração do head em `$TMPDIR`): Ran 11, OK.
- `python3 -m unittest tests.test_pedido_fora` (idem): Ran 20, OK.
- Veredito mantido: aprovado, 0 bugs. Suíte inteira: check-run `bateria` do PR neste sha.
