---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-ae2-quadro-anda
commit: 8087e23dbec99aefc234a9735132c8c5721d164d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (AE2, #875, E10.8), volta por delta

Delta lido: `forge-check parecer delta` de `cbf24de5..8087e23d`; no domínio, `bin/forge-check` (`celulas_de_cartao`, `_ler_regular(estrito)`, `linhas_de_cartao`, `montar_quadro`, `linha_movida`, mensagem de `erro_dos_atributos`), `bin/forge-fechar` (`cartoes_do_corpo`), `tests/test_fechar_move_cartao.py`, `docs/fechamento-integrador.md` e `skills/kanban-scrum/SKILL.md`. Também li `tests/test_sobreposicao_quadro.py`, que fica fora do domínio. A rodada anterior (reprovada em `cbf24de5`) está no git. Classe C.

Gatilhos: controle do Forge que analisa entrada (corpo do PR no fechamento), escrita do KANBAN.md por ferramenta, fechamento depois do merge.

## Resumo: aperta ou neutro
- **`celulas_de_cartao` (bin/forge-check:5073): aperta.** O filtro passa a ser o mesmo no quadro gerado, no aviso de edição à mão e no movimento. Ele exclui o cabeçalho (`c == COLUNAS`), o separador (todas as células casam `SEPARADOR`, também o alinhado `:--`) e as linhas de outra largura. Em `montar_quadro` e em `linhas_de_cartao` o resultado é o mesmo de antes; em `linha_movida`, o filtro aperta (antes só se exigiam `|` e 7 células).
- **Cartão em duas seções (bin/forge-check:5286): aperta.** Todas as linhas do cartão saem e a última anda.
- **UTF-8 estrito só no movimento (bin/forge-check:5304): aperta.** Com byte inválido, o movimento devolve aviso, o quadro fica intacto e o histórico é gravado. O `kanban --gerar` mantém `replace` e refaz o quadro inteiro, o que é neutro.
- **Aviso do ID fora da forma sem `[:cntrl:]` (bin/forge-fechar:954): aperta.** O ESC do corpo do PR não chega ao terminal. Os caracteres de formato Unicode (bidi) passam, mas o efeito é só visual num aviso de stderr e não há caminho de ataque: fica neutro.
- **Cartão do corpo sem coluna só avisa (bin/forge-fechar:957): aperta, com uma brecha (A5).** `coluna_do_cartao` ainda lê o KANBAN.md por um awk próprio, que não usa o filtro único. A primeira célula do cabeçalho (`ID`) conta como cartão em `Em andamento`, então `Cartão: ID` no corpo do PR passa pela guarda e cria um cartão fantasma `ID` em Pronto, com linha no histórico. Isso não corrompe o quadro (o cabeçalho fica intacto, S1; a coluna errada, S2).
- **Mensagem do `--titulo` sem `·`: neutro.** A regex de recusa é a mesma; só o texto mudou.

Achados anteriores: A1 (bloqueante) resolvido (S1, teste `test_cartao_com_nome_de_cabecalho_ou_separador_nao_casa_a_moldura`); A2 (recomendado) resolvido em parte, o resto está em A5; A3 resolvido (teste `test_cartao_em_duas_secoes_sai_das_duas` e a sonda da duplicata); A4 resolvido (teste `test_quadro_com_utf8_invalido_nao_e_reescrito` e a sonda do byte `\xff`, com os bytes preservados).

## Achados
- A5 (recomendado) bin/forge-fechar:939 · coluna_do_cartao lê o KANBAN.md sem o filtro único: a célula ID do cabeçalho dá coluna, e `Cartão: ID` no corpo do PR passa pela guarda nova e cria o cartão fantasma ID em Pronto. Pular cabeçalho e separador no awk (ou perguntar ao forge-check) e testar `Cartão: ID`.

## Sondas
- S1 · movimento com cartão `ID`, `id`, `---` e `:--` (`--de — --para Pronto --`, quadro com separador `|:--|` em Pronto) · espera: cabeçalhos e separadores intactos e uma linha nova do cartão · obtido: rc 0, cabeçalhos=2 e separadores=2 nos quatro casos, e a linha nova do cartão no fim de Pronto
- S2 · `coluna_do_cartao ID` (função extraída de bin/forge-fechar, quadro sem o cartão ID) · espera: `—` · obtido: `Em andamento` (A5); `id`, `K-9` e `Cartão` devolvem `—`

## Detalhe
**A5.** Evidência: `bin/forge-fechar:939` (o awk compara `c[2] == id` em toda linha que começa com `|`) e `bin/forge-fechar:957` (a guarda confia nessa coluna). Caminho: o autor do PR põe `Cartão: ID` no corpo, como exemplo ou por engano. O ID passa pela forma, `coluna_do_cartao` devolve a seção da primeira tabela e o `movimento ID --de "Em andamento" --para Pronto` cria a linha `ID` em Pronto e grava o histórico. O impacto fica nas métricas e na integridade do quadro, sem acesso. Severidade baixa. Como o A2 era recomendado, este resto continua recomendado. Correção mínima: no awk do KANBAN.md, ignorar a linha cujo `c[2]` é `ID` e `c[3]` é `Cartão`, e as linhas cujas células são todas separador; ou fazer a coluna sair do `forge-check`, pelo mesmo `celulas_de_cartao`. Somar `Cartão: ID` ao teste `test_cartao_do_corpo_sem_coluna_avisa_e_nao_nasce_em_pronto`. Esforço P. Dono: autor do #875 (tech-lead).

Suíte: no CI do head `8087e23d`, a catraca está vermelha e as baterias pendentes, porque faltam os pareceres desta rodada. Rodei `tests.test_fechar_move_cartao` e `tests.test_sobreposicao_quadro` no head: 96 testes, OK. As sondas foram scripts locais (biblioteca padrão e bash), com o quadro em pasta temporária.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, testes do repositório e sondas locais. A varredura de segredos não se aplica ao delta, que não traz credencial nem configuração nova.
