---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp14-definicao
commit: 0f921872cf4e8f854bfc7ccefab316da3fd046e3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0480-bp14-definicao (BP14, E163.4)

Escopo: diff `998e2e45..0f921872` (3 arquivos: `docs/retrospectivas/_modelo.md:9`, `templates/projeto/docs/retrospectivas/_modelo.md:9`, `changelog.d/v0480-bp14-definicao.md`). Pergunta do brief: o portão da retro segue sem contar o comentário, e a mudança só aperta ou é neutra?

## Gatilhos
Gatilhos: modelo lido pelo portão da retro (`forge-check retro --pendentes`), só texto dentro de comentário HTML; nenhum hook, guarda, workflow ou código tocado.

## Achados

## Sondas

## Detalhe dos achados
- Portão da retro: neutro. A linha alterada continua um comentário HTML de uma linha só, que abre com `<!--` e fecha com `-->` na mesma linha; `bin/forge-check:6080` só conta como corpo a linha que não começa com `<!--`, então a seção "Dados do pedido" do modelo segue sem corpo e o modelo copiado sem preenchimento não cobre versão. Prova: `tests/test_retro_pendentes.py:107` (`test_retro_so_com_o_cabecalho_do_modelo_nao_cobre`) passa no head.
- Os dois modelos seguem byte a byte iguais (`cmp` sem diferença; `tests/test_retro_pendentes.py:113` confere).
- Texto: aperta. "Pedido parado" passa de termo solto a critério verificável (aberto, sem movimento no quadro há 7 dias ou mais), o que reduz a margem para omitir um pedido da tabela pedido × não entregue; nada sai do comentário (a marca de `R-DECISAO`, a idade e a linha `nenhum` continuam).
- Neutralidade (`R-NEUTRO`): o texto novo não cita projeto, stack nem nome próprio.
- Fragmento de changelog: só texto, tipo `Adicionado`, aceito pelo `bin/forge-changelog`.

Testes dos arquivos tocados, locais no head: `python3 -m unittest tests.test_retro_pendentes` com 20 testes OK. A suíte inteira fica com o CI do PR.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do diff, `grep`, `cmp`, o teste citado; varredura de segredo não se aplica (diff só de texto, sem credencial).
