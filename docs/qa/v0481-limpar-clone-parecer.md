---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-limpar-clone-parecer
commit: 86f50b244f7b814d8733a656aae8c1d9111c1df5
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481-limpar-clone-parecer (#890, E14.12, classe C, volta única)

Escopo: delta `fe1f2275..86f50b24` (1 commit de código, E14.10): `limpar_clones` em `bin/forge-fechar` (linha 693, exclusão `refs/tags/arquivo/*`), `tests/test_forge_fechar.py`, `tests/test_fechar_limpar_clone.py`, as specs de mutantes e o passo 7 da doc. Clone de QA em `/root/.forge-contrib/wt/v0481-limpar-clone-parecer-qa`, no sha revisado. Os achados A1 (afrouxamento da tag local) e A2 (catraca cega) do parecer anterior (`fe1f2275`) estão resolvidos: o teste da base `test_commit_so_em_tag_local_fica` voltou idêntico (o `git diff 8833d0f6..HEAD -- tests/test_forge_fechar.py` não remove linha alguma), então não há afrouxamento nem perda de asserção; `tests/catraca.py --modo regras --base 8833d0f6 --head HEAD` sai 0.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| tag `arquivo/*` (da origin) fora da conta do `rev-list` | `LimparClones.test_commit_so_em_tag_arquivo_nao_prende_o_clone` | tag com prefixo `arquivo/` | passou; prova (H ok, B falha) |
| outra tag local com commit exclusivo segura o clone (como na base) | `LimparClones.test_commit_so_em_tag_local_fica` | tag de outro nome | passou; herdado da base (guarda restaurada) |
| ancestral do head MERGED conta como mesclado, sem a ref remota | `LimparCloneNaoListado.test_parecer_ancestral_do_head_mesclado_sai_sem_a_ref_remota` | ref remota apagada | passou; prova (H ok, B falha) |
| commit depois do head mesclado fica | `LimparCloneNaoListado.test_commit_do_clone_depois_do_head_mesclado_fica` | logo fora do limite | passou (herdado, guarda de borda) |
| stash e branch local sem envio ficam | `test_stash_fica`, `test_commit_nao_enviado_em_outra_branch_fica` | stash, branch local | passou (herdado) |

## Vermelho antes do verde
`bin/forge-testes --vermelho 8833d0f69953017f4c5947d4c5f8dc33aca55bfa --modulos tests.test_forge_fechar,tests.test_fechar_limpar_clone` saiu 0:
```
vermelho: base=8833d0f69953 head=86f50b244f7b módulos=test_forge_fechar,test_fechar_limpar_clone (restrito por --modulos)
tests.test_fechar_limpar_clone.LimparCloneNaoListado.test_parecer_ancestral_do_head_mesclado_sai_sem_a_ref_remota · H=ok · B=falha · prova (asserção)
tests.test_forge_fechar.LimparClones.test_commit_so_em_tag_arquivo_nao_prende_o_clone · H=ok · B=falha · prova (asserção)
tests.test_forge_fechar.LimparClones.test_commit_so_em_tag_local_fica · H=ok · B=ok · não prova (passa na base)
contagem: não prova (passa na base)=44; prova (asserção)=2
```

## Mutantes
`bin/forge-mutante tests/mutantes/v0481-limpar-clone-parecer.json` saiu 0:
```
forge-mutante: pedido=v0481-limpar-clone-parecer rev=86f50b244f7b spec=c40fb26c733a9f8645f15bf05454996f089c4b6de581a3fbe52c27fc64ce0e68
M1 · morreu · bin/forge-fechar:693
M1b · morreu · bin/forge-fechar:693
M2 · morreu · bin/forge-fechar:697
```
`bin/forge-mutante tests/mutantes/v0474-mp6-disco-3.json` (o M18 realinhado) saiu 0: `M17`, `M18` (`bin/forge-fechar:693`) e `M19` morreram. As duas linhas de guarda mudadas (693 e 697) têm mutante; a exclusão ampla (M1b) morre pelo teste da tag local, e a remoção da exclusão (M1) morre pelo teste da tag `arquivo/*`. Nenhum sobrevivente.

## Sondas (rodadas de novo)
`python3 -I /workspaces/.forge-contrib/qa-v0481-limpar-sonda-tags.py` (subclasse de `LimparClones`, ambiente do próprio teste): 23 testes, OK.
- S1 tag anotada `marco-local` num commit não enviado: o clone fica (como na base).
- S2 tag `arquivo-x` (quase-nome, hífen): fica. S3 `arquivox/t`: fica. S4 `meu/arquivo/t` (prefixo no meio): fica.
- S5 tag anotada `arquivo/anot`: sai (rc 0, clone apagado).
Conclusão: o commit só numa tag local de outro nome segura o clone, como na base; só o prefixo exato `refs/tags/arquivo/` sai da conta.

Risco residual aceito, sem achado: tag criada à mão no clone com nome `arquivo/*` e commit exclusivo é apagada junto. É o recorte que o review e a segurança pediram, e o fluxo do Forge só cria essa tag a partir da origin.

## Cenários e resultado real
Suíte completa: não rodada localmente (vale o check-run do CI do PR). Lido no #890 neste momento (`gh pr checks 890`): `catraca` pass, `bateria (passos)` pass, `bateria (pareceres)` fail (9 s) e as partes da suíte ainda pendentes. O `bateria (pareceres)` vermelho é provavelmente o parecer de review e o de segurança ainda no sha `fe1f2275` (o QA, regravado agora, acompanha o head); não verifiquei o log. Sem E2E nem acessibilidade (sem tela).
