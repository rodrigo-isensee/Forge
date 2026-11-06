---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/doutor-f8-caminho
commit: 85c5b80d7f42889d0d26f413fd3a22c31ac4d732
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033 (doutor F8, caminho do passo a passo)

Revisão estática do commit 85c5b80 sobre b45e40a: `bin/forge-doutor` (+3 -1), `changelog.d/doutor-f8-caminho.md` e `tests/test_doutor_protecao_gh.py`. Na rodada 1 (parecer `doutor-034`, em 4bfc92e), o texto do aviso não teve achado. A novidade aqui é conferir se o arquivo existe antes de citá-lo.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `bin/forge-doutor` é o diagnóstico do plugin. A mudança só escolhe o texto do aviso da F8. Não mexe em rede, permissão nem decisão: a branch sem proteção continua indo para `problemas` do mesmo jeito.

## Achados
- A1 (recomendado) bin/forge-doutor:378 · `Path.is_file()` segue symlink (faz `stat` no alvo). Não lê o conteúdo e o texto cita só o caminho fixo; o único efeito de um link para fora da raiz é escolher entre duas frases. Sem caminho de ataque; registrado por completude.

## Detalhe dos achados
- Leitura do conteúdo: a checagem (`bin/forge-doutor:378-379`) chama só `(raiz / c).is_file()` e não abre o arquivo. Ela só monta o texto do aviso (linha 390).
- Caminho: os dois candidatos são constantes do código, `docs/engineering/protecao-de-branch.md` e `docs/protecao-de-branch.md`. Nada vem de entrada externa, então não há travessia de diretório. O texto impresso é o caminho constante, nunca o alvo do link nem o conteúdo.
- Symlink (A1): `is_file()` faz `stat` seguindo o link. Um symlink versionado no repositório e apontando para fora da raiz faria o doutor revelar só um booleano (se o alvo é arquivo regular), e só ao próprio usuário local, na saída do comando. Um FIFO ou dispositivo dá `False`, sem bloquear, porque `stat` não abre o arquivo. Quem versiona o link já controla o repositório inteiro. Não há atacante nem ganho, por isso a severidade é **informativa**. Correção mínima, opcional: `not p.is_symlink() and p.is_file()`. Esforço P. Dono: implementador do doutor.
- Falha segura: `is_file()` devolve `False` para caminho inexistente, `ENOTDIR` e laço de symlink. Só uma falta de permissão no `stat` levantaria exceção, e em `docs/` do próprio projeto isso não é realista. A checagem roda só no `forge doutor` completo (`bin/forge-doutor:409-410`, fora do `--rapido`): o hook `doutor.py`, que usa o modo rápido, nunca a executa. Sem o arquivo, o aviso cita a skill `ci-cd`, como antes.
- Testes: `python3 -I -m unittest discover -s tests -p test_doutor_protecao_gh.py` deu 15 OK em 85c5b80. Os testes cobrem os dois caminhos e o caso sem arquivo.

## Riscos aceitos e ferramentas
Nenhum risco aceito; A1 é recomendação que não devolve a entrega (`R-REVIEW`). Usei leitura do diff e os testes acima. Lacuna: `gitleaks` e `semgrep` não estão no PATH. O diff não traz credencial, dependência nem rede nova (`R-CUSTO`).
