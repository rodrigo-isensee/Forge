---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0480-d6c-idioma-ordens
commit: 66c9f9a1869ca39537b97be3a3e70c73456ec93b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E1.4, revalidação por delta do PR #866)

Regravação no pedido v0481. A rodada anterior (E174.15, `commit: 0c7e8f0c`, aprovado, `pedido: v0478`) fica no git. O commit revisado é o Revisar-sha `66c9f9a1` (o merge da develop); o head lido é `92263857`, que depois dele só traz os pareceres de review e QA.

Gatilhos: hook que injeta contexto a cada fala do dono (`hooks/ordens.py`), leitura de arquivo de configuração do projeto.

## Delta lido
`forge-check parecer delta` (`0c7e8f0c..92263857`, sem o que veio da develop): no domínio, só `tests/test_hooks.py:2650-2666`, o teste do vigia de prazo vindo do merge da develop (`a27eab7e`, #859, com o seu próprio parecer); fora, `docs/hooks-fixtures.md` (índice gerado, único conflito do merge). `git diff 0c7e8f0c 92263857 -- hooks/ordens.py tests/hooks/ordens tests/mutantes/v0480-d6c-idioma-ordens.json` vazio: o código e o corpus do pedido não mudaram.

Do merge, `hooks/_comum.py` muda `prazo_vencido` e `executar` (o vigia arma também sem `critico`, quando há `regra_do_prazo`). `hooks/ordens.py:129` chama `executar("ordens", principal)` sem `regra_do_prazo`: `prazo_s` segue `None`, o vigia não arma e o hook das ordens não ganha caminho novo de recusa nem de silêncio.

## Achados anteriores
- A1 (bloqueante, rodada E174.8): segue **corrigido**; `hooks/ordens.py` sem mudança desde `0c7e8f0c`.

## Só aperta ou neutro, por escrito
O item segue **neutro**: o delta não toca o hook das ordens nem o seu corpus, e a mudança do vigia vinda da develop não alcança o `ordens` (sem `regra_do_prazo`). O veredito da rodada E174.15 se mantém.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Ferramentas: `forge-check parecer delta`, leitura do diff. No head `92263857`: `python3 -m unittest -k OrdensEmVigor tests.test_hooks`, 23 testes OK, e `test_vigia_prazo_trava_sem_marcador_recusa_e_fora_da_sessao_vigiada_libera` OK. A suíte inteira roda só no CI; o CI verde do PR #866 segue obrigatório para o merge.
