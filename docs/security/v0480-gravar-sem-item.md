---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-gravar-sem-item
commit: e77e13e88b11df8c820004ec37392296ee174708
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 E90.27 (G1.2a, corte (a): `autorizacao gravar` sem o alvo `item:`)

Gatilhos: autorização do dono (ADR 0018), controle do Forge (`R-SEGURANCA`).

## Resumo
O head e77e13e8 é o corte (a) do G1.2a, tirado da develop fc488261. Ele traz o `gravar` revisado na `melhoria/v0479-sieg-g1-gravar` (parecer aprovado 50a3022d, head d4960f8e) sem a parte do alvo `item:`. A rodada anterior fica no git. Aqui li o diff `fc488261..e77e13e8` inteiro e o comparei com o código revisado (`git diff 50a3022d e77e13e8`).

- **O corte é um subconjunto do revisado.** `bin/forge-testes`, `changelog.d/`, `docs/indice-forge.md` e `tests/pesos-d4.json` não mudam em relação ao revisado. Em `bin/forge_autorizacao.py` só saem `ponta_do_ramo` (devolvida para dentro de `fora_do_revisado`, com a mesma lógica), `commit_do_ramo` e o ramo `item:` de `concessao_lida`. Em `bin/forge-check` só sai a opção `--ramo`. Nenhuma linha nova de lógica entra. O `mensagem_do_dono`, a `leitura`, o `gravar_novo` (`O_EXCL` e `O_NOFOLLOW`, 0600), o `pedido_aberto` e as duas mudanças do `ler` são byte a byte os já aprovados.
- **O alvo `item:` sempre recusa no `gravar`.** `ALVOS` (`bin/forge_autorizacao.py:26`) só aceita `item:<CARTAO>` sozinho, sem mistura com `pr:` ou `versao:`. Com `item:`, `problemas` chama `do_item` (`:144`). Como `concessao_lida` não preenche mais `Commit` (`:380`), `do_item` sempre devolve "Commit não é sha de 40 caracteres" (`:171`), qualquer que seja o ato ou o texto. A recusa vem antes do `mkdir` e do `M-<uuid>` em `cmd_gravar` (`:389`), então nada é gravado. O teste `test_o_que_o_leitor_recusaria_nao_e_gravado_alvo_item_nesta_etapa` (`tests/test_autorizacao_gravar.py:339`) cobre isso: rc 1, a mensagem de recusa e nenhum `A-*` gravado.
- **Mutantes:** saem os do alvo `item:`, que deixaram de ter código. Um mutante do `ler` em `tests/mutantes/v047-sieg-g1-autorizacao-6.json` muda o trecho `de` para continuar único, porque o `gravar` repete a expressão. O alvo da mutação e o teste que a mata continuam os mesmos.
- **Achados anteriores:** os da rodada da `v0479-sieg-g1-gravar` continuam fechados, porque o código deles não mudou. A ressalva já escrita na ADR 0018 também continua: a origem da transcrição não está provada (`:286`, a sessão vem do ambiente), e a pasta de concessões aceita escrita direta. Isso só fecha no corte do hook, e hoje nada consome concessão. Fora `forge-check autorizacao` (`ler`), nenhum hook nem `bin/forge-fechar` lê `.forge/autorizacoes/` (busca em `hooks/`, `bin/forge-fechar` e `bin/forge-check`).

**Só aperta? Sim, por escrito.** No head e77e13e8, em relação à base fc488261, o item não aceita nada que antes era recusado. No `ler`, a fala no futuro passa a ser adulterada (`:237`), e emoji ou letra de outra escrita passam a contar como palavra fora do vocabulário (`:157`). As duas mudanças só acrescentam recusa ou pendência. O `gravar` é novo e grava só o que o `ler` já leria. Ele recusa todo alvo `item:`. Também recusa a fala fora das 48 h, a transcrição fora da sessão e o que não tem `origin` humano. O prazo local e o fim de pedido não registrado nascem pendentes. A concessão gravada não destrava nenhum portão nesta etapa. Contra o revisado na `v0479-sieg-g1-gravar`, o corte só retira o caminho que podia gravar o alvo `item:` como ativo. Pelo lado da segurança, o rótulo pela regra do dono até 27/11 vale para este item no head e77e13e8.

**Explorável antes dos próximos cortes?** Não. Nada consome concessão ainda.

## Riscos aceitos e ferramentas
Nenhum risco aceito. A suíte inteira não rodou aqui e o PR ainda não existe: o brief pede só os testes dos arquivos tocados, e o CI do PR será o portão. Rodei `tests/test_autorizacao_gravar.py` e `tests/test_autorizacao.py`: 45 testes OK. Não rodei `gitleaks` nem `semgrep`. O diff só retira código de um trecho já revisado e não traz segredo nem dependência nova.
