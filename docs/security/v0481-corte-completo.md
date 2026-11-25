---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-corte-completo
commit: 036a78a16d09a3abf29ae94c02d4e6665e2b5227
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E13.18, #887, forge-fechar --corte: marca pronta para a promoção; classe C)

## Gatilhos
Gatilhos: controle do fluxo de merge e de release (`forge-fechar --corte`, R-FLUXO, R-MAIN), envio a ramo no origin, rótulo do dono (R-CONTRIB).

## Lido
`git diff 5fb8e328..036a78a1`: `bin/forge-fechar` (+92/-14: `medir_a_marca`, `corpo_da_marca`, `fragmentos_em`, `anexar_na_marca`, `rotulo_da_promocao` e as chamadas no `corte_da_versao`), `tests/test_fechar_corte.py`, as specs de mutante, `tests/pesos-d4.json`, `docs/fechamento-integrador.md` e o fragmento. Sem parecer anterior nesta branch.

## Achados
- A1 (bloqueante) tests/test_fechar_corte.py:369 · CI vermelho no Revisar-sha: test_reval_delta.Guarda acusa README.md citado 3 vezes em tests/test_fechar_corte.py e a lista CITACOES_CONHECIDAS (tests/test_reval_delta.py:124) diz 2; sem CI verde não atesto o head. Correção: atualizar a contagem (ou reaproveitar a citação). Dono: autor.

## Sondas
- S1 · sonda em arquivo (subclasse de tests.test_fechar_corte.Corte): marca cortada, `changelog.d/item-0.md` editado na develop e `changelog.d/novo.md` novo, `forge-fechar --corte` · espera: para no V5 sem enviar nem `pr edit` · obtido: rc 1, "parou no passo V5: o fragmento novo não entrou na marca da 0.9.1", ramo no origin igual, nenhum `pr edit`
- S2 · mesma sonda: marca 0.9.1 mesclada na develop, homolog e main, ramo `melhoria/marca-0.9.1` deixado no origin, fragmento novo, `--corte` · espera: o ramo velho não recebe fragmento da versão seguinte · obtido: rc 0, "contador: 0.9.2: 1 de 2", ramo 0.9.1 intocado, nenhum `pr edit`

## Detalhe (só aperta ou neutro, por escrito)
- **Nenhum merge sem checks verdes.** O diff não acrescenta `gh pr merge` nem `--auto`; o único merge novo é o `git merge` local da `origin/develop` na cópia temporária do ramo `melhoria/marca-<v>` (bin/forge-fechar:1549-1551), enviado só por avanço (`git push origin HEAD:refs/heads/$ramo`, sem `--force`). O PR da marca segue pelo `--laco`, que exige pareceres no head e checks verdes; o head novo invalida os pareceres anteriores (aperta). O `test_fechar_corte.sem_merge` cobre os caminhos do corte.
- **O anexo não leva fragmento de outra versão.** `v` sai do contador da `origin/develop` (versão do `plugin.json` + 1), então o ramo da marca mesclada não é mais o da versão corrente (S2). Novos = fragmentos da `origin/develop` ausentes da base comum dela com o ramo (:1541-1542), que é exatamente o que entrou na develop depois do corte; depois do anexo a base comum vira a ponta da develop e a volta seguinte não faz nada (teste). Fragmento já cortado e editado na develop conflita (modificado × apagado) e para sem enviar (S1).
- **Nada que barra deixa de barrar.** A medida roda antes do envio e a falha dela para sem enviar (:1624, `test_marca_que_nao_mede_nao_envia`): aperta. Ramo já no origin: antes voltava 0; agora anexa ou para, e a leitura em erro (`r=erro`) segue sem anexar (:1614): neutro ou aperta. `forge-check` e `forge-changelog` vêm do `bin/` do script com `python3 -I`, não da cópia mesclada: o código do ramo não executa. A linha `teto: excedido, <n> linhas, marca de versão` é escrita só quando o teto é excedido, com `<n>` medido pelas funções do próprio `forge-check` (`contagens_do_intervalo` e `forge_tamanho`); o 1c continua exigindo `<n>` de pelo menos o total medido na promoção, e a medida refeita no anexo acompanha o head: neutro (a guarda confere uma declaração; quem a escreve agora é o script, com o número real).
- **Rótulo.** `rotulo_da_promocao` (:1562-1568) só lê os rótulos (`gh pr list ... --json labels`) e imprime `gh pr view <url> --web`; não aplica rótulo nem traz o comando dele, e a leitura que falha só avisa: neutro (R-CONTRIB intacto).
- **Data local** (:1622): `date +%F` muda só o texto da seção; neutro.

## Riscos aceitos e ferramentas
Nenhum risco aceito. CI do Revisar-sha: suíte parte 3/5 vermelha nas duas versões do Python (A1), demais partes verdes. Rodei `python3 -m unittest tests.test_fechar_corte` (28 testes, OK) e as sondas S1 e S2. gitleaks, shellcheck, zizmor, actionlint e semgrep ausentes no PATH (lacuna; o delta não toca workflow nem segredo). Revalidação: com A1 corrigido e o CI verde, o delta só de teste não muda a análise acima.
