---
tipo: revisao-seguranca
contrato: 1
pedido: pn4-decisao-aprovacao
branch: melhoria/pn4-decisao-aprovacao
commit: e2f3390adad9be87cca02a42d37bde2411812ff4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-30
---
# Review de segurança: pn4-decisao-aprovacao

Escopo: revalidação por delta (`forge-check delta`) do parecer anterior, sobre `8ebaa95..e2f3390` (volta 1 da P-N4): `bin/forge-check` (`hora_da_aprovacao`, chamada em `avaliar_brief`), `tests/test_decisao_aprovacao.py`, `tests/mutantes/pn4-decisao-aprovacao.json`. O resto do diff `add00ab..e2f3390` não mudou desde a revisão anterior.

## Gatilhos
`R-SEGURANCA`: controle do Forge (o `forge-check brief` é portão do brief, `R-BRIEF`); `docs/kanban/conferencias.md` é entrada desse portão.

## Achados
- A2 (recomendado) hooks/conformidade.json:1 · docs/kanban/conferencias.md segue sem dono no hook: qualquer papel escreve a tabela que decide; restringir ao jarvis no cartão KANBAN-DONO-HOOK (hooks/ fora do escopo).
- A3 (recomendado) bin/forge-check:4342 · a coluna do pedido (c[1]) da linha aprovado não é conferida; exigir c[1] igual ao id do pedido do brief, junto do A2.

## Detalhe dos achados
**A1 (anterior, resolvido).** `bin/forge-check:4339-4343`: a aprovação só vale com hora >= mtime do brief no minuto, no fuso local, o mesmo de `cmd_conferencia_registrar` (`bin/forge-check:2065`). Sondas locais em pasta temporária (pedido com decisão de 11:00 faltando no brief):
- linha `aprovado` retrodatada (2000-01-01) com brief gravado agora: rc 1, decisão cobrada;
- `aprovado` 10:00 e brief reescrito depois (mtime atual): rc 1, cobrada (falha fechada no `touch`);
- brief às 10:01:00 e `aprovado` 10:00: rc 1, cobrada; mesmo minuto (brief 10:00:59, `aprovado` 10:00): rc 0 com aviso, o pedido pela P-N4;
- `aprovado` 2099: nenhuma decisão é posterior, tudo cobrado; mesmo resultado com `TZ=UTC`.
Corrida do stat: o `stat` roda depois da leitura do conteúdo (`cmd_brief_conferir`, `brief mensagem`); reescrita entre a leitura e o `stat` avança o mtime e cobra tudo; remoção nesse intervalo levanta `FileNotFoundError` e o comando sai com erro, sem aprovar. Ambas falham fechadas.
Resíduo conhecido, sem bloqueio: quem escreve o brief e a tabela pode recuar o mtime (`touch -d`) e forjar a linha; isso exige escrita na tabela, que é o A2, e o conferente segue lendo as decisões.

**A2.** Mantido como recomendado, sem mudança no delta; segue no cartão KANBAN-DONO-HOOK (decisão técnica de 2026-10-30 00:46). Dono: `tech-lead`, esforço P.

**A3.** Sonda: linha `aprovado` com outro pedido na coluna 2, mesmo nome de brief e hora válida, dispensa a decisão posterior (rc 0, aviso). Sem caminho de ataque fora do A2: o nome do brief já carrega o id do pedido, e a linha precisa ser escrita à mão. Correção: em `hora_da_aprovacao`, receber o id do pedido e exigir `c[1].casefold()` igual a ele. Dono: `tech-lead`, esforço P.

## Sem achado
- Fuso: registro e conferência usam a hora local da máquina; fuso diferente entre os dois processos só desloca a janela em horas e exige controlar o ambiente do `conferencia registrar`.
- Brief por link simbólico: `stat` e leitura seguem o mesmo alvo.
- Os chamadores sem `brief` (`bin/forge-check:1527`, `:5049`) seguem cobrando tudo.
- Mutantes M14 (sem a guarda do mtime) e M15 (`>` estrito) cobrem a guarda nova; a suficiência é do QA.
- PA-7: AR-3, AR-5 e AR-7 não se aplicam (nenhum subprocesso, trava de ambiente ou pasta do git nova).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática e sondas locais em pasta temporária; `tests.test_decisao_aprovacao` verde (7 testes). `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH (lacuna registrada); nenhuma dependência ou workflow mudou.
