---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/heredoc-prazo-pendentes
commit: fd63c19af38b7719c4d97ea96376fa68475f349a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: heredoc-prazo-pendentes (HEREDOC-DONOS-AJUSTES S-A2, frente 0.34)

Revalidação do HEAD `17bed08` (código em `9614094`), sobre `melhoria/heredoc-donos-fronteira` (`d943cd3`). É a metade S-A2 da antiga `heredoc-donos-ajustes` (`3bdb360`, aprovada na volta 1). Somadas, as duas metades dão em `hooks/` o mesmo diff da antiga, só com outros deslocamentos de linha.

## Gatilhos
Controles do Forge (hook `conformidade`: vigia de prazo e corpos pendentes, C-4): R-SEGURANCA.

## Achados

## Detalhe dos achados
Sem achados. Antes de `tirar_heredocs`, os `<<` da linha entram em `corpos_pendentes` (`hooks/conformidade.py:757-758`) e saem na mesma conta logo depois (`len(corpos) - provisorios`, `:779`), inclusive no ramo do `ValueError`. O `prazo_vencido` só libera sem marcador quando `corpos_pendentes` está em zero. Com isso, o prazo que vence na janela da tirada passa a recusar. `<<<` e `<<` entre aspas só superestimam a conta nessa janela, o que deixa a decisão mais estrita. O delta de teste traz `test_prazo_vencido_na_tirada_dos_heredocs_ja_os_acha_pendentes` e o mutante `tests/mutantes/hook-conformidade-034-7.json`.
A forma juntada da `hook-continuacao-linha` chama `conferir_linha` duas vezes por linha, e cada chamada faz a sua soma e o seu desconto. A conta fica balanceada.
A pilha herda os bloqueantes A1 a A3 de `docs/security/hook-continuacao-linha.md`. Este commit não os toca nem os agrava.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados (D-5): `tests.test_hooks.Hooks.test_fixtures`, `test_fixtures_da_trilha_034` e os testes novos da pilha. `gitleaks` e `semgrep` fora do PATH (lacuna; não instalados, R-CUSTO).
Resultado: `test_fixtures`, `test_fixtures_da_trilha_034` e os testes novos da pilha passaram (Ran 8 tests, um deles é um nome errado no comando do revisor, que o unittest acusa como ERROR do loader; não é falha do código). Parecer concluído depois da troca de conta, sobre o mesmo HEAD.

Atualização (2026-11-04): só o `commit:` passa ao HEAD `fd63c19`, reaplicado sobre a hook-continuacao-linha `a04096b`. O delta é o mesmo deste parecer; comparei com diff e só mudam os números de linha e o contexto. O veredito não muda. A pilha agora herda os bloqueantes A5 e A6 de `docs/security/hook-continuacao-linha.md` (volta 2), no lugar dos A1 a A3.
