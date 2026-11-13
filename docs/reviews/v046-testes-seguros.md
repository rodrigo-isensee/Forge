---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/testes-seguros
commit: 8fc857c94212789ba54f2db909cd09bb9325525f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-11
---
# Review: v046 (E2.2, TESTE-FORA-DO-CLONE e TESTE-REDE-ANTHROPIC)

## Escopo lido
`git diff origin/develop...ebdde388` (Base-sha ed021b71): 3 commits, 3 arquivos, +24/-1. Um commit por item (9788148f TESTE-REDE-ANTHROPIC, b7e42b80 TESTE-FORA-DO-CLONE) mais o fragmento `changelog.d/testes-seguros.md` (ebdde388). Tamanho bem abaixo da orientação M14 (23 linhas de teste). Só teste: nenhuma linha de guarda de código mudou, nenhum mutante a declarar.

## Verificação
- `tests/test_forge.py` (PrepararEstacao.test_simular_nao_instala_nada): o `claude` falso entra no `bin_falso` à frente do PATH, então a linha 351 do `scripts/preparar-estacao.sh` (`claude plugin list`) não chega à CLI real (R-CUSTO). O falso sai 1 e o teste confirma o efeito: o log tem só `plugin list` e a saída traz `[simular] claude plugin install forge@forge --scope user`. Os outros casos que rodam o script já usavam `claude` falso (`--container`) ou saem antes (`--x`).
- `tests/test_pedido_fora.py` (Fora.test_travessia_e_link_para_fora_sao_recusados): `rodar_em` fixa o `cwd` em `tmp/c1/c2/c3`, onde `../../x.md` não existe, e o alvo `tmp/x.md` existe e é plantado, acessível por `../../` só a partir da raiz de brief falsa (`tmp/home/.forge-contrib`). Assim, o rc 2 só pode vir da regra de raízes de `caminho_de_brief` (bin/forge-check:3006), e não de um arquivo que falta. A ausência de `origem:` e de `conferencia-brief-regra:` prova que o brief não foi lido. Os casos `elo.md` e `outro.md` são resolvidos pelas raízes, não pelo cwd, e por isso continuam válidos com o cwd novo. Antes, o cwd herdado fazia `../../x.md` apontar para fora do clone.
- `rodar_em` repete o `rodar` de `test_voltas.Raiz` com `cwd`. É duplicação pequena e local, aceitável.

## Testes dos arquivos tocados
Rodados numa cópia do `ebdde388` (`git archive`), sem tocar na branch: `python3 -m unittest tests.test_pedido_fora`: 20 testes OK. `python3 -m unittest tests.test_forge.PrepararEstacao`: 11 testes OK. A suíte inteira fica para o CI do PR.

## Revalidação (volta 1, head 8fc857c9)
Delta lido: `git diff ebdde388..8fc857c9` (1 commit, 3 arquivos, +20/-5, só teste e fragmento; nenhuma guarda de código mudou, nenhum mutante a declarar). O `forge-check parecer delta` não serviu aqui: com o caminho absoluto recusa a raiz, e rodado de `/workspaces/.forge-contrib` responde `commit "ebdde388..." não existe` (o clone de lá não tem a branch); por isso li o diff que o brief indica.
- `NVM_DIR` com sentinela (`PrepararEstacao.test_simular_nao_instala_nada`): o teste contamina de propósito o ambiente com um `NVM_DIR` alheio cujo `nvm.sh` (não vazio, passa no `-s` de `scripts/preparar-estacao.sh:277`) deixa marca, confirma que o `ambiente_limpo` o herda e fixa `NVM_DIR` no HOME falso; a asserção `assertFalse(marca.exists())` prova o efeito. O mesmo `NVM_DIR` fixo entra no auxiliar do `--container`.
- `dpkg-query` falso que sai 1: a linha 256 do script passa a ler "não instalado" sem consultar o dpkg real. O comentário diz "(log à parte)", mas esse falso não grava log; imprecisão de texto, não muda comportamento.
- `test_pedido_fora`: o comentário e a nova asserção (`brief: não consegui ler`, bin/forge-check:8288) corrigem o que este parecer dizia na volta 0: de `c1/c2/c3`, `../../x.md` é `c1/x.md`, que não existe, e a recusa vem da leitura falha, não da regra de raízes. O teste segue provando o que E2.2 pede: o conteúdo plantado fora não é lido (sem `origem:` nem `conferencia-brief-regra:`) e nada é lido fora do clone.
- Testes dos arquivos tocados numa cópia do `8fc857c9` (`git archive`): `python3 -m unittest tests.test_pedido_fora tests.test_forge.PrepararEstacao`: 31 testes OK.

## Achados

## Sondas

## Parecer
Aprovado no head 8fc857c94212789ba54f2db909cd09bb9325525f (volta 1; antes, ebdde388). As duas mudanças fazem o que E2.2 pede: o teste do `--simular` não tenta mais rede com a CLI real, e o teste da travessia não lê nem depende de arquivo fora do clone. Os dois têm asserção do efeito, não só do código de saída. Commits em Conventional Commits, um por item, e fragmento de changelog presente. Sem achados na volta 0 nem na volta 1. A frase da volta 0 sobre a origem do rc 2 no caso `../../x.md` fica corrigida pela seção de revalidação.
