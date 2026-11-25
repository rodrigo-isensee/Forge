---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 50a40e28844435d4bf43c8b23d3880e1b37af7b9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Code review: hook salvar só grava na cópia local, volta E11.18 (D6 parte a; v0481 E11.19, PR #877)

Revisado por delta: `1afd54b5..50a40e28`, lido pelo `forge-check parecer delta` (escopo: sem o que veio da develop). Quatro commits do autor: `cfd24cee5` (fix, sai o envio), `b6c98cb27` (ADR, exceção do R-VERIFY só na emenda), `88fc382a7` e `50a40e288` (testes). Parecer anterior: reprovado no `1afd54b5` por A1.

- ci: 50a40e28844435d4bf43c8b23d3880e1b37af7b9 verde

## Parecer
**Aprovado.** A volta segue a DECISÃO DO DONO de 25/11 (opção b do #877): o hook só faz o commit WIP na cópia, sem rede, e o envio fica com o fechamento.

**A1 anterior (segredo em commit anterior levado pelo push): resolvido, saiu com o envio.** `salvar()` (hooks/salvar.py:133) faz só `add` e `commit --only` e lê o sha. Não há mais `push`, `fetch`, `ls-remote`, varredura nem base dela no arquivo (conferi com grep). Os bloqueantes que a segurança e o QA apontavam na base da varredura (ref local `refs/remotes/origin/<branch>`, `HEAD^` na branch nova) saíram junto. Sem envio, o segredo de qualquer commit passa pelo `pre-push` inteiro no envio de sempre.

**M8 e M9 vivos (fixture não rastreada): resolvido.** `docs/a.md2` agora é rastreado no `setUp`. Em `test_salva_so_o_escopo_na_copia` ele aparece como ` M docs/a.md2`, fora do commit, então o mutante prefixo-por-exato o levaria ao commit e morre.

**Testes do delta.** `test_branch_ja_no_remoto_fica_como_esta` prova que não há envio (a ref do remoto não muda) nem busca (a `origin/melhoria/x` da cópia não muda). `test_git_herdado_nao_desvia_a_copia` ganhou a asserção de que a cópia principal fica intacta. Saíram os testes do envio e da varredura, e os mutantes M26, M36 e M37, que guardavam linhas removidas. Nenhum mutante cita teste que não existe mais (grep em `tests/mutantes/`). O M34 segue a nova linha `fora = ("XDG_CONFIG_HOME",)`, e a saída de `BASH_ENV` e `ENV` está certa: sem o bash da varredura, nada os lê. Os remotos bare sem manutenção (`88fc382a7`) e a troca de `README.md` por `notas.txt` na fixture (`50a40e288`) só ajustam o teste às guardas `test_ambiente_git` e `test_reval_delta.Guarda`, sem mudar o que ele prova.

**ADR e R-LIMITES.** A emenda D6 diz que o item 2 da ADR 0003 segue sem exceção. A exceção ao R-VERIFY ficou só na regra 4 da emenda, que explica por que o `R-LIMITES.md` não muda: o núcleo do Jarvis não tem folga no orçamento. Este é o desenho que o brief pede ("só na emenda, fora do núcleo"). O critério de reversão passa a incluir "qualquer chamada de rede dele". O título do PR traz só `[afrouxa-regra: R-VERIFY core.hooksPath]`, coerente com o item 2 intacto.

**CI e catraca.** No head `50a40e28`, as 10 partes da suíte (3.12 e 3.14, 1/5 a 5/5) estão verdes, e também `bateria (passos)`, `bateria (verificações longas)`, `instalação`, `teto de pulados` e `árvore já provada`. Vermelhos: `bateria (pareceres)`, que espera os pareceres; `bateria`, que agrega; e `catraca`. Pelo log (run 45652375891), a catraca falha no R-QA, em guardas de `hooks/salvar.py` sem mutante que as prove: a 127 (M29, declarado só como equivalente) e a 156 (`__name__ == '__main__'`). As duas linhas vêm de antes deste delta (a catraca do `1afd54b5` também falhou), e o delta não as toca. Esta é a falha que o rótulo `afrouxa-regra` do dono libera, rótulo que o PR já pede pelo R-VERIFY.

**Verificadores.** Rodei `python3 -m unittest tests.test_hooks.SalvarAoParar`, `Hooks.test_hooks_json` e `Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia` no `50a40e28`, com ambiente limpo: 31 testes, OK. Apliquei à mão o M34 (`fora = ()`) numa cópia do `50a40e28` (`git archive`), e `test_config_global_de_fora_nao_roda` falhou, ou seja, o mutante morre. Não rodei o `bin/forge-mutante` porque a trava `pesado` estava ocupada por outra sessão. A suíte inteira é a do CI citado, e não rerrodei o SHA. **Teto:** o delta tira linhas do hook (27 linhas mudadas em `hooks/salvar.py`, saldo negativo), então o excedido já aceito não cresce.
