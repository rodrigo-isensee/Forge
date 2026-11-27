---
tipo: qa
contrato: 1
pedido: release-0.47.20
branch: melhoria/v0481-release-0-47-20-pareceres
commit: 779356dcee5f1c840e328dc6efbd3fa9275e8d77
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: release 0.47.20 (E43.4, revalidação E1.10) (versão 0.47.20, head 779356dc)

QA da leva `main..1e301536` (PR #935, 26 commits, 23 itens: #909, #910, #913, #914, #916 a #934). Marca `3bf1456e` mais o #933 e o #934, anexados por merge da develop `8855671d`. Modelo: `docs/qa/release-0.47.19.md`. Os itens já têm parecer de QA em `docs/qa/`; não rerrodei a suíte (R-QA, G3).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão nos dois manifestos igual ao CHANGELOG | `plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.20; `## [0.47.20] - 2026-11-27` | manifestos iguais | passou |
| `[Não publicado]` vazio, seção em português | CHANGELOG linhas 5 a 7 | seção acima da 0.47.19 | passou |
| `changelog.d/` sem fragmentos | `bin/forge-changelog conferir-release`: ok | só `README.md` | passou |
| Os 23 itens estão na seção | 24 entradas (Adicionado 7, Alterado 9, Corrigido 8) para 23 itens | nenhum a menos | passou |
| Testes dos módulos tocados pela junção | `test_changelog` e `test_conferir_release`: 108 OK (33 s) | n/a | passou |
| CI do head | `gh pr checks 935`: rc=0, suíte 5/5, instalação 3.14, catraca, pareceres, passos, longas verdes | n/a | passou |
| Sem teste pulado indevido | nenhum `skip` novo achado no diff da junção | n/a | passou |
| 7 regras afrouxadas (#909, #918, #920, #928, #929, #931, #932) | commits e títulos trazem `[afrouxa-regra: ...]` com motivo; rótulo `afrouxa-regra` em 6 de 7 | destaque, motivo, aceite | passou, com A1 e A2 |
| Pareceres dos itens | QA aprovado dos itens em `docs/qa/` (17 arquivos no diff) | n/a | passou |

## Revalidação do delta 8855671d..779356dc (E1.10)
Delta: #936 (50e5b609, encolhe o #930), #937 (eba76f80, F1p2 C1a), #935 (marca) e #939 (anexo dos fragmentos). Base do parecer anterior: head 1e301536.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Anexo no CHANGELOG: fragmentos do #936 e #937 na 0.47.20, `changelog.d/` só com README | diff do CHANGELOG entre 447b4ad2 e 779356dc: +1 entrada em Adicionado (#937), +1 em Corrigido (#936); `ls changelog.d`: README.md | nada a menos, nada fora da seção | passou |
| Versão nos manifestos inalterada (0.47.20) | diff dos dois `plugin.json` entre 447b4ad2 e 779356dc vazio | manifestos iguais | passou |
| #937: conta aceita é a dona do origin; registro das publicações | mutantes `v0481-f1p2-c1a*.json` (3 specs): 18 de 18 morreram, rc=0 | recusa de outra conta; status sem registro | passou |
| Testes dos módulos tocados (`test_forge_pareceres`, `test_changelog`, `test_conferir_release`) | 195 OK em 31 s | n/a | passou |
| #936: guarda de grafia do Bash sai; Write/Edit e caminho literal ficam | `hooks/conformidade.py` com 75 linhas a menos, 15 fixtures `raiz-forge-*-bloqueia` removidas, 1 renomeada para `-libera`; `test_hooks` roda no CI | caminho literal bloqueia; grafia fica com o sandbox | passou pelo CI; local interrompido por mim aos 300 s, sem veredito |
| CI | `gh pr checks 939` (head f61936bf): suíte 5/5, bateria, instalação 3.14, catraca, pareceres, passos, longas verdes; na develop, `checagem rápida` e `árvore do PR já provada` de 779356dc success | n/a | passou |

Tabela de regras afrouxadas do PR da main (A1): passa de 7 para 8 itens. O #936 afrouxa (título `[afrouxa-regra]` e rótulo; a grafia do Bash passa ao `denyWrite` do SO) e entra na tabela com motivo e aceite do dono. O #937 leva o rótulo `afrouxa-regra` por tocar arquivo protegido, mas não afrouxa regra (a conta aceita fica mais estrita e há registro novo): entra como "rótulo por arquivo protegido, sem afrouxar", fora da contagem. Os #938 e #940 seguem abertos e fora da leva.

## Execução
- Cópia própria em `~/.forge-contrib/wt/v0481-release-0-47-20-qa-engineer`, head igual ao remoto.
- Sem tela: acessibilidade n/a. Segurança e review têm parecer próprio.
- ci: 779356dcee5f1c840e328dc6efbd3fa9275e8d77 verde (PR #939, head f61936bf, verde fora bateria (pareceres), bateria e catraca; push na develop de 779356dc success)

## Parecer
Aprovado no head 779356dc: marca, junção, CHANGELOG e o delta (#936, #937, #939) conferem. Os dois achados abaixo são do texto do PR da main e do rótulo, não do código.

## Achados
- A1 (recomendado) docs/qa/release-0.47.20.md:1 · o corpo do PR da main deve listar as 8 regras afrouxadas (#909, #918, #920, #928, #929, #931, #932 e #936) com o aceite do dono, e o #937 como rótulo sem afrouxar; o corpo do PR da main deve trazer a tabela "Itens que afrouxam regra", como na 0.47.19.
- A2 (recomendado) docs/qa/release-0.47.20.md:1 · o #918 (ato `rotulo-pelo-time`) tem `[afrouxa-regra]` no título mas não o rótulo `afrouxa-regra`; as outras seis têm. Confirmar com o dono antes do merge na main.
