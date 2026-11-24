---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-trava-critica
commit: cf8b8f696d2acb4431d62506b5f0667f25fad698
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E169.5, PR #853)

Escopo: diff `0f4a7791..cf8b8f69` (E169.1, E169.2): `hooks/_comum.py` (`prazo_vencido`, comentários de `marcado` e do vigia), fixtures `tests/hooks/conformidade/errointerno-prazo-sem-escrita-bloqueia.json` e `vigia-prazo-trava-gh-com-aspas-bloqueia.json`, `tests/test_hooks.py`, `tests/mutantes/v0480-vigia-trava-critica.json`, ADR 0003, ADR 0009, `docs/hooks.md` e o fragmento do changelog.

## Gatilhos
Gatilhos: controle de hook que decide recusar ou liberar (falha fechada por prazo, ADR 0009 seção 7)

## Achados

## Sondas

## Detalhe dos achados
Conclusão por escrito: a mudança **só aperta**; nenhuma linha que antes recusava passa a liberar.

- **O que mudou.** `hooks/_comum.py:2860` tira do retorno antecipado a isenção `hook.marcado is False and not hook.corpos_pendentes`. Antes, com o prazo vencido, a linha sem o marcador crítico e sem corpo de heredoc pendente liberava (ex.: `"g"h repo create x --public`, que não casa o marcador); agora recusa pela regra do hook. O ramo dos corpos pendentes (C-4) segue recusando, só muda a ordem da escolha do texto (`:2862-2864`). Os demais retornos (`critico is None`, `PostToolUse`, sessão não vigiada) já existiam e ficaram iguais: o conjunto que libera encolheu, nunca cresceu.
- **Saídas que ainda liberam, conferidas uma a uma:**
  - *Hook sem marcador (`critico is None`).* Em `executar` o vigia só arma com `regra_do_prazo` e `critico` (`hooks/_comum.py:2894`); sem eles, `prazo_s` é None, o alarme não arma e `PrazoVencido` não sobe. O ramo é inalcançável pelo `executar` e serve só de defesa da função. Os hooks sem marcador que recusam antes da ferramenta (`agentes`, `pesado`) não têm vigia e dependem do `timeout` do `hooks.json`; isso é anterior ao PR, não muda aqui, e as duas travas de segurança (`conformidade`, `parecer`) têm vigia (`hooks/conformidade.py:4506`, `hooks/parecer.py:1354`). Não é caminho de contorno aberto por esta mudança.
  - *PostToolUse.* A ação já rodou; recusar depois não a desfaz. No `conformidade` o PostToolUse só grava a autoria do parecer (`hooks/conformidade.py:4487-4492`); se o prazo vencer ali, a autoria fica sem registro, e o `forge-check pr` trata parecer sem autoria como violação (`bin/forge-check:2055`). Falha para o lado fechado; não serve de contorno.
  - *Sessão não vigiada.* `sessao_vigiada` (`hooks/_comum.py:254-271`) é a mesma decisão da falha fechada (`falhar_fechado`, `:2789`) e da identificação da sessão: fora de projeto e de `~/.forge-contrib` nenhuma trava age, com ou sem prazo; exceção na decisão vale como vigiada. Mudar a raiz ou a pasta para sair da sessão vigiada desliga a trava inteira, não só o prazo: não é contorno novo, e o PR não o alarga.
- **Disponibilidade.** Linha legítima lenta sem marcador passa a ser recusada numa sessão vigiada, com o contorno no texto (`CONTORNO_DO_TETO` ou `contorno_do_prazo`). É o efeito pedido pela decisão do dono (VIGIA-PRAZO-TRAVA) e falha para o lado seguro. O texto diz "a chamada com ação crítica" também para a linha sem marcador; é questão de redação, sem efeito de segurança (fica com o `tech-lead`, se quiser).
- **Provas.** `python3 -m unittest` dos três testes tocados (`test_vigia_prazo_trava_sem_marcador_recusa_e_fora_da_sessao_vigiada_libera`, `test_fixtures_do_vigia_prazo_trava`, `test_prazo_vencido_com_corpo_de_heredoc_pendente_recusa`) no head: 3 testes, OK. `bin/forge-mutante tests/mutantes/v0480-vigia-trava-critica.json` no head: M1 a M5 morreram (M1 devolve a isenção antiga; M2 a M4 tiram cada saída que libera; M5 troca o texto). Suíte inteira: no CI do PR #853 (em andamento quando este parecer foi escrito; o merge depende dele verde).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, busca no código, testes e mutantes do próprio PR. Segredo e SAST fora do escopo do diff; as ferramentas de varredura não estão no PATH deste ambiente (lacuna registrada, sem efeito neste diff).
