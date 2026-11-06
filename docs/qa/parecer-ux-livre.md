---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/parecer-ux-livre
commit: a061a495677e611fe38ee127d6b53fb225c02e11
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# Parecer de QA - PARECER-UX-LIVRE (E9, L05)
Base dc615c25a89cf801dbff0356ff3e07cf491e4567; código a061a495677e611fe38ee127d6b53fb225c02e11; head testado c7a2ae0fdbdf9ddd31dd2420d9e414ace1c877fa (só pareceres depois do código). Review e segurança aprovados.

## Escopo
`docs/ux/` entra em `LIVRES` de `bin/forge-check`: o parecer segue válido depois de commit só nessa pasta e perde a validade com qualquer outro caminho (R-REVIEW, R-QA). Sem tela: acessibilidade e E2E não se aplicam.

## Tabela obrigação -> teste -> resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Commit só em `docs/ux/` mantém o parecer | `test_commit_so_em_docs_ux_nao_invalida`; sonda: vários arquivos e subpasta | pasta e subpasta | passa |
| Commit de código sozinho invalida | sonda `bin/forge-x` | fora da lista | passa (rc 1) |
| `docs/ux/` junto de outro caminho invalida | `test_docs_ux_mais_um_byte_em_bin_invalida`; sonda com `docs/outro.md` | mistura | passa (rc 1) |
| Renome de `hooks/` para `docs/ux/` invalida | `test_renome_de_hooks_para_docs_ux_invalida` | `--no-renames` | passa |
| Renome de `docs/ux/` para `src/` invalida | sonda | saída da pasta | passa (rc 1, cita `src/x.md`) |
| Nomes parecidos (`docs/ux-x/`, `docs/UX/`, `docs/uxa.md`) invalidam | `test_nomes_parecidos_invalidam` | prefixo e caixa | passa |
| Lista exata de `LIVRES` | `test_livres_tem_exatamente_estas_entradas` | sem entrada extra | passa |
| Merge da develop só com `docs/ux/` | `test_merge_da_develop_so_com_docs_ux_nao_invalida` | merge | passa (guarda o E4, ver A1) |

## Execução real
- `python3 -m unittest tests.test_forge.PareceresComDocsUx`: 6 testes, OK, rc=0. Sonda minha (fixtures `RepoComOrigem`, 4 casos acima marcados "sonda"): 4 testes, OK.
- `forge-testes --vermelho dc615c2 --modulos test_forge`: estourou o prazo de 500 s (rc 124), sem veredito. Vermelho à mão, `bin/forge-check` da base numa cópia: 3 de 6 falham (livres exatas, commit só em docs/ux, renome), os outros 3 são de abuso e passam na base por desenho.
- Mutação (cópia): `docs/` no lugar da entrada: 4 falhas; `docs/ux` sem barra: 3 falhas; sem a entrada: 3 falhas. Nenhum sobrevive. `forge-mutante --cobertura --base dc615c2`: rc 0, nenhuma condição mudada (só constante).
- `scripts/validar-plugin.sh`: Validation passed. `bin/forge-check docs`: rc 0.
- Suíte inteira não rodada: o review rodou `tests.test_forge` (488, OK) no código a061a49 e só a classe é tocada (R-TETO).

## Achados
- A1 (recomendado) tests/test_forge.py:4916 · o teste do merge passa sem a entrada em `LIVRES` (traz também `src/y.txt`); já apontado no review e na segurança.

## Parecer
Aprovado: sem bug aberto. A consequência aceita pelo dono (commit em `docs/ux/` sem revisão nova) é a decisão do E9.
