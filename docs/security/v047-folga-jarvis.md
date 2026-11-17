---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-folga-jarvis
commit: 6288db934914dcf2ce14bae404987057dbe7b48c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047 (folga do texto do Jarvis, revalidação E2.674)

Revalidação por delta `2a95b163..6288db93` (`forge-check parecer delta`: "nenhum arquivo do domínio mudou"; fora: `tests/fixtures/diretrizes-do-dono-exemplo.md`, `tests/test_jarvis_nucleo.py`). Li o commit `6288db93` inteiro (3 linhas no teste e o exemplo novo). A rodada anterior (2a95b163, invariantes e arquivos novos da falar-com-o-dono) fica no git; os achados seguem abaixo com o estado.

Gatilhos: `R-SEGURANCA`, controles do Forge (`tests/config.json`, rodada anterior; o delta não o toca).

**Nada afrouxou.** `test_cada_numero_do_arquivo_do_dono_tem_entrada` (`tests/test_jarvis_nucleo.py:243`) trocava a falta de `FORGE_DIRETRIZES_DONO` por `skipTest`; agora lê `tests/fixtures/diretrizes-do-dono-exemplo.md` (1 a 29) e roda `problemas_das_diretrizes(..., numeros)` (`tests/apoio_jarvis.py:98`). Com a variável apontando para um arquivo, confere o arquivo real como antes. A asserção e a função não mudam; no CI, onde antes pulava, a checagem passa a exigir entrada para 1 a 29: mais estrita, não menos. Com a variável apontando para um caminho inexistente, cai no exemplo em vez de pular; antes também não falhava.

**Neutralidade (`R-NEUTRO`).** O exemplo só traz "diretriz de exemplo N" e uma frase de formato, sem nome, regra de negócio nem conteúdo do arquivo real do dono (que segue fora do git); `Neutralidade` de `tests/test_forge.py` passa (6, OK).

Suíte: sem CI neste head; rodei `tests.test_jarvis_nucleo` sem `FORGE_DIRETRIZES_DONO` (43, OK, sem skip) e `-k Neutralidade tests.test_forge` (6, OK). O CI do PR continua obrigatório para a integração.

## Achados
- A1 (recomendado) tests/apoio_jarvis.py:84 · corrigido no 8a223677; o delta não toca o arquivo. Sem pendência
- A2 (recomendado) tests/fixtures/diretrizes-do-dono.json:164 · diretrizes 26 a 28 como pendente (MAX_PENDENTES = 7); sem mudança no delta; decisão de escopo sem caminho de ataque, ao dono pelo Jarvis (`R-DECISAO`)

## Detalhe dos achados
A1 e A2 sem mudança desde o parecer do 2a95b163. Nenhum achado novo no delta; nenhum bloqueante; sem sonda nova (nenhum bloqueante a provar).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, a biblioteca padrão do Python e os testes do repositório. `gitleaks` ausente no PATH (lacuna); o delta é um teste e um arquivo de exemplo sem credencial.
