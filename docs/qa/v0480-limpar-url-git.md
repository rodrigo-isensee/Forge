---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-limpar-url-git
commit: 2186affb75a57c4f74d07e10e0affac332f25be0
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0480-limpar-url-git (PR #851, E166.4)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E166.1: clone sem `.git` no origin é da mesma origin | `test_clone_sem_ponto_git_e_da_mesma_origin` | `.git` final | passou; cai na base |
| E166.1: clone com barra final | `test_clone_com_barra_final_e_da_mesma_origin` | barra final | passou; cai na base |
| E166.1: cópia com `.git/` contra clone sem os dois | `test_copia_com_ponto_git_e_barra_casa_com_o_clone_sem_os_dois` | os dois sufixos, lado invertido | passou; cai na base |
| E166.1: outro origin fica pendente, avisa, não apaga, não vaza URL | `test_clone_de_outro_origin_fica_pendente_e_avisa` | origin diferente (rc 3, sem `rm -rf`) | passou; cai na base |
| Regressão: o teste antigo de outro origin migrou | `test_clone_de_outra_branch_nao_e_tocado` | outra branch | passou |

## Cenários e resultado real
Vermelho antes do verde (`forge-testes --vermelho f94876069cb5 --modulos test_fechar_limpar_clone`):

```
vermelho: base=f94876069cb5 head=da8e0173362e módulos=test_fechar_limpar_clone (restrito por --modulos)
revertidos à base: bin/forge-fechar, changelog.d/v0480-limpar-url-git.md
...clone_com_barra_final_e_da_mesma_origin · H=ok · B=falha · prova (asserção)
...clone_de_outro_origin_fica_pendente_e_avisa · H=ok · B=falha · prova (asserção)
...clone_sem_ponto_git_e_da_mesma_origin · H=ok · B=falha · prova (asserção)
...copia_com_ponto_git_e_barra_casa_com_o_clone_sem_os_dois · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=5; prova (asserção)=4
```

Mutantes (`bin/forge-mutante tests/mutantes/v0480-limpar-url-git.json`, rc 0): U1 a U7 morreram. A lista cobre cada linha de guarda mudada em `bin/forge-fechar` (comparação normalizada, `${1%/}`, `${u%.git}`, `copia_st=pendente`, aviso, `continue`).

Execução real do `--limpar`: os três testes `com_origins` rodam `forge-fechar --limpar` num clone real com `.git` na URL da cópia e sem ele no clone (e o inverso); saem `limpeza: remota=ok worktree=ok branch=ok clone=ok` e o clone é apagado.

Testes dos arquivos tocados, locais: `test_fechar_limpar_clone.py` 9 testes OK; `test_forge_fechar.py` 34 testes OK. A suíte inteira fica para o check-run `bateria` do CI do PR.

## Revalidação por delta (E166.8, head 2186affb)
forge-check parecer delta: intervalo da8e0173..2186affb; no domínio só tests/mutantes/v0474-mp6-disco.json e v0474-mp6-disco-2.json (commit a5e738b1: M8 aponta o teste renomeado; M9 aponta a linha nova do origin com url_normal e o teste test_clone_de_outro_origin_fica_pendente_e_avisa).

bin/forge-mutante tests/mutantes/v0474-mp6-disco.json tests/mutantes/v0474-mp6-disco-2.json: rev=2186affb75a5, M1 a M16 (sem M11) todos morreu; M8 (bin/forge-fechar:627) e M9 (bin/forge-fechar:629) mortos. Sem sobrevivente.

ConferirTodas, test_fechar_limpar_clone e test_forge_fechar: 47 testes OK. A suíte inteira fica para o check-run bateria do CI.

Observação sem bloqueio: com `url_aqui` vazio (leitura do origin da cópia falhou), o clone da branch agora também fica pendente com o aviso. Isso é mais seguro que o silêncio anterior e coerente com o objetivo.
