---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-catraca-avisos
commit: 7b107cfd7bc8bc61303e894731e91e5818050156
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E14.39, #897, primeira rodada; classe C)

Lido: `b224ee09..7b107cfd` inteiro (`tests/catraca.py`, `tests/test_catraca.py`, `tests/mutantes/v0481-catraca-avisos.json`, `changelog.d/v0481-catraca-avisos.md`). Sem parecer anterior nesta branch.

Gatilhos: controle do Forge (a catraca, que decide o bloqueio por teste afrouxado e a liberação pelo rótulo do dono; R-CONFORMIDADE).

- ci: 7b107cfd7bc8bc61303e894731e91e5818050156 verde

## Conferência
- **Só aperta ou neutro, por escrito: neutro.** As três mudanças em `tests/catraca.py` são `print` e um parâmetro de texto; nenhum ramo de decisão, retorno ou código de saída muda:
  - `:757` `onde` entra por último, com padrão, só como texto; as chamadas são o recuo (`:776`, que não o passa e não pode estourar de novo com teto infinito) e `_testes_por_modulo` (`:811`). O `print` (`:775`) vem antes do mesmo `return testes_da_arvore(arvore, 0, math.inf)` de antes: o perfil devolvido é o mesmo (o teste novo confere 0 asserções no ajudante com o teto estourado).
  - `:2264-2265` as linhas `catraca: liberada:` saem depois da decisão `liberado` e antes do mesmo `return 0`; o caminho que barra (`:2267-2270`) não mudou.
  - Falha do `print` (pipe fechado, codificação): exceção não tratada sai com código diferente de 0, ou `OSError` cai em `FALHAS_DO_GIT` (`:1323`) e vira violação. Em qualquer caso barra mais, nunca solta.
  - Na PR, o CI roda a catraca da base (`CATRACA_DA_BASE`, `.github/workflows/catraca.yml`), não a deste head: a mudança não age sobre a própria PR.
- **Vazamento no log público do CI: nada novo.** `onde` é o caminho do módulo e a ref, já impressos no log (checkout, diff). Cada `v` liberado é o mesmo texto que o resumo do job já grava (`:2262`) e que o caminho que barra imprime cru em `:2268`; vem só do conteúdo do repositório (caminhos, nomes de teste, regras), nunca da resposta da API nem do token. Comando de workflow (`::`) embutido num nome de caminho já chegava ao início de linha em `:2268`; aqui vem atrás do prefixo `catraca: liberada: `. O job tem `contents: read`, `pull-requests: read`, `actions: read`.
- **Outros leitores do stdout:** `bin/forge_corrigidos.py:153` chama `violacoes_das_regras` e imprime texto para pessoa; os `python3 -I -` de `bin/forge-fechar` (`par_de_promocao`, controles tocados) não chegam a `testes_da_arvore`. Nenhum consumidor faz parse do stdout do caminho tocado: a linha a mais não muda decisão de ninguém.
- **Mutantes:** `bin/forge-mutante tests/mutantes/v0481-catraca-avisos.json` no `7b107cfd7bc8`: CAV1 (`:775`), CAV2 (`:811`) e CAV3 (`:2265`) morreram; `--conferir --base b224ee09` confere os trechos no lugar.
- **Testes:** os dois novos (`AssercaoNoAjudante.test_teto_estourado_avisa_o_modulo_e_o_que_contou`, `LinhaDeComando.test_liberada_pelo_rotulo_nomeia_cada_violacao`) → OK; `python3 -m unittest tests.test_catraca` inteiro → 417 testes, OK. A suíte inteira roda no CI do PR #897 no mesmo head: as 10 partes da suíte, passos, verificações longas, instalação e teto de pulados verdes. Vermelhos só os que esperam parecer ou rótulo: `bateria (pareceres)` (R-REVIEW, pareceres ainda ausentes), `bateria` (o agregador, por ela) e `catraca` (R-CONFORMIDADE, mudança em `tests/catraca.py`, pede o rótulo `afrouxa-regra` do dono). O merge exige todos.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, o módulo de teste tocado e `bin/forge-mutante` (nada externo). Varredor de segredos, SAST e auditor de dependências não se aplicam ao delta, que não traz dependência nem segredo.
