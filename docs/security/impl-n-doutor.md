---
tipo: revisao-seguranca
contrato: 1
pedido: impl-n-doutor
branch: melhoria/impl-n-doutor2
commit: eb6db50ffddaa4d53e0aba23348b24b70d242b3c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-22
---
# Review de segurança: impl-n-doutor

Etapa E1.3 do pedido `docs/pedidos/impl-n-doutor.md`, sobre a branch refeita `melhoria/impl-n-doutor2` (base `a3dbe22`, HEAD `eb6db50`). Requisito: o adendo `docs/security/ameacas/n-doutor.md` (controles e casos de abuso). O parecer anterior (`8f32f37`) era da branch antiga `melhoria/impl-n-doutor` e não vale para esta; este parecer o substitui e cobre só o diff `a3dbe22..eb6db50`.

## Gatilhos
- `hook` e `rede nova`: RELOGIO-WSL (`hooks/doutor.py:117`, `bin/forge_versoes.py:182-251`).
- `credencial`: item 62 (`bin/forge-doutor:267-297`).
- `chamada ao gh`: aviso da F8 (`bin/forge-doutor:319-389`).
- `apagar pastas da máquina` (M11): **fora desta entrega**. O M11 não tem commit na branch (registro no Histórico do pedido: sem cache de plugin na máquina, o passo 0 não foi feito). Nada a revisar; os controles CM-1 a CM-14 do adendo continuam requisito do cartão M11-CACHE, e o M11 sem o passo 0 segue não revisável.

## Achados

## Detalhe dos achados
Nenhum bloqueante. Conferência controle a controle do adendo:

**Item 62 (sem o nome da chave de API, P-A = A).**
- C62-1 e C62-5: a lista fixa `SINAIS_DE_CUSTO` (`bin/forge-doutor:267`) tem três nomes, sem o nome da chave de API, e a frase só junta nomes dessa lista e `apiKeyHelper` (`bin/forge-doutor:281-297`); nenhum valor, chave arbitrária ou trecho de arquivo vai ao texto. `git grep` no HEAD: o nome da chave de API só aparece nos testes da catraca que já existiam, nada novo no diff, nem montado.
- C62-2: `apiKeyHelper` só por presença; nunca executado nem impresso (teste do arquivo-sentinela em `tests/test_doutor_custo.py:45`).
- C62-3: `ler_json` (`bin/forge-doutor:50-70`) abre sem bloquear, exige arquivo regular pelo descritor já aberto (sem corrida entre conferir e ler) e lê no máximo 1 MiB + 1 byte; JSON inválido, não-objeto e `env` fora do formato viram ausência, e cada fonte falha sozinha. Sonda em cópia própria: atalho para `/dev/zero`, para pasta e para pipe sem escritor dão "ilegível" em 0 s.
- C62-4 e C62-6: vazio ou só espaço conta como ausente; a frase diz "pode estar"; os testes conferem o marcador fora de stdout, stderr, `.forge/run/*` e `erros.log`, também no SessionStart.

**RELOGIO-WSL.**
- CR-1: `HEAD` pelo cliente HTTP de baixo nível da biblioteca padrão (não segue redirecionamento, não usa proxy do ambiente, não lê corpo), contexto TLS padrão com certificado obrigatório, só `User-Agent` fixo (`bin/forge_versoes.py:218-224`); testes conferem método, uma conexão só no `302`, ausência de credencial e `CERT_REQUIRED`.
- CR-2: `host_publico` (`bin/forge_versoes.py:182`) recusa IP literal (inclusive formas curtas e decimais), `localhost`, nome sem ponto, porta diferente de 443 e usuário na URL; sem conexão aberta (testado).
- CR-3: prazo total pela espera da linha de execução (`bin/forge_versoes.py:229`), além do prazo por operação; falha não marca o dia (`hooks/doutor.py:139-142`).
- CR-4 e CR-6: `Date` com até 100 caracteres, só com fuso explícito, teto de 30 dias vira None; o texto usa minutos calculados aqui, nunca o cabeçalho; o cache guarda só a frase, nunca o desvio nem o cabeçalho.
- CR-5: `FORGE_RELOGIO_REMOTO` só com `FORGE_PERMITE_LOCAL=1` (`bin/forge_versoes.py:206`), testado nos dois sentidos.
- AR-7: `FORGE_VERIFICAR_VERSAO=0` faz `url_do_forge()` devolver None, e o hook nem consulta com a consulta de versão desligada ou falha.

**Aviso da F8.**
- C8-1 e C8-2: `--method GET` explícito, dois endpoints fixos mais o `repo view`, branch de lista fixa; `nameWithOwner` por `fullmatch`, sem segmento começando com `-` nem só de pontos (`bin/forge-doutor:372-375`); os casos A8-1 e A8-5 estão nos testes (`tests/test_doutor_protecao_gh.py`).
- C8-3 e C8-4: três estados; `404` só vira "sem proteção" com a mensagem de branch sem proteção, depois de o `repo view` ter respondido; `403`, `404` de repositório e formato inesperado viram "não consegui conferir".
- C8-5, C8-6 e C8-7: o aviso nunca ecoa a saída do `gh` (teste com marcador); `GH_HOST` diferente ou `url` fora de `https://github.com/` não consulta; só no modo completo, nunca no hook nem em `--rapido` (testado). C8-8: nenhuma sugestão paga.

**Testes sem rede e sem `gh` real (R-CUSTO).** Sonda: cópia do HEAD em `$TMPDIR`, com a abertura de conexão de rede do interpretador trocada por erro registrado (herdada pelos subprocessos), rodando `tests.test_doutor`, `tests.test_doutor_custo`, `tests.test_doutor_relogio`, `tests.test_doutor_protecao_gh` e `tests.test_atualizar`: 173 testes OK, **zero** tentativas de conexão. O `gh` dos testes é sempre o falso da `Base` ou o do próprio teste. Os toques em `tests/test_doutor.py` (fixture do `gh` falso por endpoint, `env` sem os nomes de custo herdados) e em `tests/ambiente_git.py`, `tests/apoio_versao_defasada.py` e `tests/test_atualizar.py` só isolam o ambiente; nenhum afrouxa teste existente.

**Recomendações (não bloqueiam):**
- R1 (informativa) `bin/forge-doutor:345`: a regra de ruleset sem o campo `enforcement` conta como ativa. Isso se apoia na semântica do endpoint de regras por branch (devolve só as regras ativas); se um dia a resposta trouxer regras em modo de avaliação sem o campo, o doutor ficaria mudo. Correção mínima, se o dono quiser endurecer: campo ausente vira "não consegui conferir" (C8-3 pede isso para formato inesperado). Esforço P; dono: tech-lead.
- R2 (informativa) `bin/forge_versoes.py:182`: nome público que resolve para endereço interno (por exemplo, serviços de DNS que devolvem o IP do próprio nome) passa no filtro. Exige controlar `FORGE_REPO_URL` no ambiente do dono, e o ganho é só um `HEAD` sem credencial; sem caminho realista, fica registrado. Esforço P; dono: tech-lead.
- R3 (informativa, herdada do adendo T62-5): `ANTHROPIC_BASE_URL` num settings de repositório de terceiro continua sem sinal; é decisão do dono se vira item futuro.

## Riscos aceitos e ferramentas
- Riscos aceitos: nenhum neste parecer. O aceite do risco da camada de ancestral sem `/proc` (CM-10) pertence ao M11, que não está nesta entrega.
- Ferramentas: leitura do diff `a3dbe22..eb6db50`, `git grep`, sondas na biblioteca padrão em cópia própria em `$TMPDIR`, sem rede. Faltaram no PATH (lacuna, nada instalado): `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint`, `trivy`, `shellcheck`. A entrega não toca workflow, contêiner nem dependência; nenhum segredo foi lido ou exibido.
