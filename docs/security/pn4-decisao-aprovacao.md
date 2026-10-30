---
tipo: revisao-seguranca
contrato: 1
pedido: pn4-decisao-aprovacao
branch: melhoria/pn4-decisao-aprovacao
commit: 8ebaa9540c4019591558de816c0bda8775250cee
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-30
---
# Review de segurança: pn4-decisao-aprovacao

Escopo: diff `add00ab..8ebaa95` (P-N4): `bin/forge-check` (`hora_da_aprovacao`, `decisao_posterior`, `decisoes_cobradas`, `conferir_decisoes`), `bin/forge-testes`, `tests/test_decisao_aprovacao.py`, `tests/mutantes/pn4-decisao-aprovacao.json`, `tests/test_testes_tocados.py`, fragmento do changelog.

## Gatilhos
`R-SEGURANCA`: controle do Forge (o `forge-check brief` é portão do brief, `R-BRIEF`). A mudança faz uma linha de `docs/kanban/conferencias.md` passar a dispensar decisões do dono: essa tabela vira entrada de portão.

## Achados
- A1 (bloqueante) bin/forge-check:4340 · segurança (entrada de portão sem origem nem vínculo ao conteúdo): qualquer linha `aprovado` com o nome do brief vale, mesmo escrita à mão, retrodatada, de outro pedido ou anterior à última escrita do brief; exigir hora da aprovação >= mtime do brief.
- A2 (recomendado) hooks/conformidade.json:1 · docs/kanban/conferencias.md não está em `caminhos`: qualquer papel escreve a tabela que agora decide; restringir a escrita ao jarvis em pedido próprio (hooks/ fora do escopo da P-N4).

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:4336-4343` aceita como aprovação qualquer linha de tabela com `c[2]` igual ao nome do brief, `c[3] == brief`, resultado que começa com `aprovado`/`cumpriu` e hora no formato; não confere a coluna do pedido (`c[1]`), nem a autoria, nem que a aprovação é posterior ao texto do brief que se confere; e vale a última linha `aprovado` mesmo com um `reprovado` depois dela. `docs/kanban/` não tem dono em `hooks/conformidade.json` (ver A2), e `conferencia registrar` não é o único escritor possível. Sondas (cópia do `test_decisao_aprovacao` em pasta temporária, brief gravado agora, decisão faltante de 2026-01-01 11:00):
- linha escrita à mão `| 2000-01-01 00:00 | outro | exemplo-dev-exemplo-1 | brief | 9 | aprovado | ... |` (retrodatada, pedido de outro): rc 0, a decisão faltante sai só como `decisão posterior à aprovação`;
- `aprovado` 10:00 seguido de `reprovado` 12:00 do mesmo brief (brief reescrito e reconferido): rc 0, aviso;
- resultado `aprovado? não`: rc 0, aviso; nome com caixa e `.md` (`Exemplo-Dev-Exemplo-1.md`): conta como o mesmo brief (aceitável);
- nome parecido (`-10` para `-1`), hora com `T` ou com segundos: não valem, cobrado tudo (correto).
Caminho de ataque: um subagente (papel `dev` ou outro, sob injeção de prompt vinda de conteúdo do repositório) acrescenta uma linha à tabela com o nome previsível `<pedido>-<destino>-<n>` e hora antiga; daí em diante toda decisão do dono com data e hora deixa de reprovar esse brief no `forge-check brief` e no `brief mensagem`, e um brief sem uma restrição nova do dono passa pelo portão mecânico só com aviso. O mesmo vale, sem má-fé, para um brief reescrito depois de aprovado: herda a aprovação do texto antigo. O conferente ainda lê as decisões, por isso a severidade é média, não alta; mas é o portão determinístico que deixa de cobrar.
Correção mínima (dono: `tech-lead`, esforço P), dentro de `hora_da_aprovacao`: a aprovação só vale se a hora dela for maior ou igual ao mtime do arquivo do brief, arredondado para baixo ao minuto e no fuso local (o mesmo de `cmd_conferencia_registrar`); senão devolve None (cobra tudo, como hoje). Isso fecha a linha retrodatada, a de outro brief com o mesmo nome e o brief reescrito depois da aprovação (o `chmod 0444` do registro não muda o mtime); uma linha forjada com hora posterior à última escrita do brief só dispensa decisões que o texto do brief não podia conter, que é o comportamento pedido pela P-N4. Testes: linha retrodatada (anterior ao mtime) cobra tudo; brief reescrito depois da aprovação cobra tudo; aprovação no mesmo minuto da escrita vale. Opcional no mesmo commit: exigir `c[1]` igual ao id do pedido e só `aprovado` exato (sem `cumpriu`, que é veredito de entrega).

**A2.** Evidência: `hooks/conformidade.json` tem dono para `docs/pedidos/`, `docs/briefs/` e as pastas de parecer, e nenhum para `docs/kanban/`. Antes da P-N4 a tabela só alimentava contagens (`voltas`, `classes`, `rodadas`); agora alimenta um portão. Severidade baixa depois de A1. Correção: entrada `docs/kanban/conferencias.md` (e as cópias sob a raiz dos pedidos) com `quem: ["jarvis"]`, em pedido próprio, porque hooks/ está fora do escopo deste pedido. Dono: `tech-lead`, esforço P.

## Sem achado
- Formato da hora: `HORA_DO_REGISTRO.fullmatch` na aprovação e `HH:MM` com `\b` na decisão dão comparação lexicográfica de cadeias de mesmo formato; hora igual segue cobrada (`>` estrito); decisão sem hora, com data `(AAAA-MM-DD)` ou com hora de um dígito segue cobrada. Fuso: ambos locais à máquina do Jarvis; diferença de fuso só tornaria a regra mais conservadora ou atrasaria a dispensa em horas, sem caminho de ataque.
- Leitura da tabela por `_tabela_segura` (`O_NOFOLLOW`, teto de bytes, `errors=replace`): link ou arquivo grande dão lista vazia, logo sem aprovação e cobrança total.
- Brief sem aprovação continua cobrado contra tudo (`test_sem_aprovacao_cobra_tudo`); a decisão posterior continua visível como aviso, com o texto passado por `nome_seguro` e cortado em 60 caracteres.
- Os outros chamadores de `decisoes_cobradas` (`bin/forge-check:1527`, `:5048`) não passam `brief` e mantêm a cobrança total.
- PA-7: AR-5 (python sem `-I`) e AR-3 não se aplicam (nenhum subprocesso novo, nenhuma trava de ambiente); AR-1 e AR-2 são do QA.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática e sondas locais em pasta temporária. `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH (lacuna registrada); nenhuma dependência ou workflow mudou.
