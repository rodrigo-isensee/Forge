---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-limpar-clone
commit: 7ba9f0bac3d84e0b231995b8e50778404b0ca179
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E132.10, PR #831, conserto do fechamento: E132.6, E132.7 e E134.2)

Review do PR #831 no head 7ba9f0ba, só o diff contra a develop (base 0ed441e9): `bin/forge-fechar` (72 linhas, abaixo do teto H1), uma linha do mapa em `bin/forge-testes`, `tests/test_fechar_limpar_clone.py` (4 testes), casos novos em `tests/test_fechar_busca_pareceres.py` e `tests/test_fechar_longas.py`, o campo `clone=nenhum` nas asserções de resumo, duas specs novas de mutante, duas specs ajustadas, fragmento em `changelog.d/` e pesos.

## O que foi conferido
- Merge da base (7ba9f0ba, cinco conflitos): `git show --remerge-diff 7ba9f0ba` só tira as linhas do lado da develop nos cinco arquivos (`bin/forge-fechar`, `bin/forge-testes`, a spec de busca-pareceres, `tests/pesos-d4.json`, `tests/test_fechar_busca_pareceres.py`); nenhuma linha nova na resolução, nenhuma lógica nova.
- E132.6 (LIMPAR-CLONE-NAO-LISTADO): o clone sai com HEAD ancestral de um head mesclado (`merge-base --is-ancestor` nesta cópia, depois da busca dos mesclados) ou com o sha conferido; o commit fora das refs remotas do clone é refeito nesta cópia contra as pontas lidas agora (`ls-remote`), e um commit que esta cópia não lê faz o `rev-list --stdin` falhar e o clone ficar. Leitura da origin que falha deixa `pontas` vazio, e o clone fica (teste com `ls-remote` falso que sai 1). A mudança só aperta: o caso antigo da ref remota de branch apagada segue valendo. O campo `clone=` sai sempre (`nenhum`), como o pedido manda.
- A1 e A2 do review E132.2: busca por metades (9 fetches para 16 sha com um ausente, teste conta as chamadas); `--principal` vazio, com `--promover` ou com `--limpar` é erro de uso, cada um com teste.
- E132.7: `test_lsremote_exato_um_ajudante_unico_le_a_branch_remota` igual ao da develop (sem diff) e verde; as pontas passam pelo `remoto_exato --pontas`, a única chamada de `ls-remote`.
- E134.2: a alternância `integra(c|ç|Ç)(a|ã|Ã)o` casa em `C`, `POSIX` e `C.UTF-8` (subtestes com as duas grafias); mutante M12 volta ao colchete e morre.
- Testes dos arquivos tocados: `python3 -m unittest tests.test_fechar_limpar_clone tests.test_fechar_busca_pareceres tests.test_fechar_longas` com 21 testes OK. Mutantes: `bin/forge-mutante --processos 1` nas duas specs novas, M1 a M12 morreram; uma guarda nova por mutante (as linhas de `||`, `&&` e `return` do diff), cada uma com teste de comportamento do ramo de falha.
- CI do PR no head (run 45311318404): `bateria (verificações longas)` vermelho no shellcheck (A1); a suíte ainda corria quando o parecer foi escrito.

## Achados
- A1 (bloqueante) bin/forge-fechar:607 · `local -a sem` cria a variável `sem`, e o shellcheck passa a ler `st=sem-pass` (:532) como aritmética (SC2100, warning): o job `bateria (verificações longas)` do CI cai. Renomear (ex.: `sem_busca`) zera o SC2100 (conferido com o shellcheck 0.10.0); rodar o shellcheck antes do envio.
- A2 (recomendado) tests/test_fechar_config.py:104 · o nome `..._a_linha_da_limpeza_nao_ganha_campo` contradiz a asserção nova, que agora espera o campo `clone=nenhum`; renomear o teste para o que ele confere.

## Sondas
- S1 · shellcheck 0.10.0 em bin/forge-fechar no head 7ba9f0ba · espera: sem SC2100 · obtido: SC2100 em :532 (st=sem-pass); com `sem` renomeado para `sem_busca` o SC2100 some

## Parecer
Reprovado. A lógica das três etapas está correta e coberta por teste e mutante, e o merge da base não trouxe lógica nova; o único bloqueio é o A1, o shellcheck vermelho no CI provocado pelo nome da variável nova. A volta é de uma linha (o nome em `origem_atual`, :607, :610 e :611), com o shellcheck local verde antes do envio; o A2 vira cartão depois do merge.
