---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-g3-partes-iguais
commit: 4c0b3842edfc6916e013bc5fcef7f749a094493f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E102.6, fatias de test_fixtures e do T1 de variantes)

Base 2d73a35e, head 4c0b3842. Diff: `tests/test_hooks.py` (teste de controle, classe C), `tests/pesos-d4.json`, `changelog.d/v0480-g3-partes-iguais.md` e o review do tech-lead. Sem mudança em `hooks/`, `scripts/` nem `.github/`.

## Gatilhos
Gatilhos: teste de controle dos hooks de conformidade (cobertura das fixtures e do T1 de HOOK-COMENTARIO-SHLEX, ADR 0013).

## Achados
- A1 (recomendado) tests/test_hooks.py:2685 · test_t1_as_fatias_cobrem_todo_o_corpus recopia o fatiamento `corpus[k::FATIAS_DO_T1]` em vez de chamar o mesmo código da linha 2704; se o fatiamento do T1 mudar só lá, o teste de cobertura continua verde. Extraia `corpus_da_fatia(k)` e use nos dois, como já faz `fixtures_da_fatia`.
- A2 (recomendado) tests/test_hooks.py:190 · Nada liga FATIAS_DE_FIXTURES e FATIAS_DO_T1 aos métodos test_*_fatia_N: subir a constante para 5 ou apagar um método deixa uma fatia sem rodar com os testes de cobertura verdes. Confira que existe um test_fixtures_fatia_{k+1} e um test_t1_fatia_{k+1}_... para cada k.

## Sondas

## O que foi conferido
- Nenhuma fixture sai da verificação: `fixtures_da_fatia` (`tests/test_hooks.py:742`) reparte `self.fixtures` por `i % 4`, e as 4 fatias têm método próprio (`:755` a `:765`). A ordem é a mesma em todo processo e runner (`sorted(FIXTURES.glob(...))`, `:737`), então as partes do CI não se sobrepõem nem deixam buraco. Cada fatia mantém a asserção `executar_em_lote(...) == len(fatia)` e recusa fatia vazia.
- Nenhuma fixture passou a pular: o pulo segue só no `pular_sem_ns_de_pid` de antes, e no CI nada pula (`:802`). As fixtures de prazo de produção continuam fora, como antes (`test_prazo_do_merge`).
- Nenhuma linha do corpus do T1 sai: o corpus (`_CORPUS`) vem das fixtures em ordem e o filtro não mudou; as 4 fatias `[k::4]` cobrem tudo, e o `minimo(_CORPUS, 500)` continua valendo para o corpus inteiro. As variantes (`VARIANTES_QUE_O_BASH_IGNORA`) e as asserções do laço não mudaram.
- Piso de linhas por variante: o de antes (`lidas >= 500 * V` no total) vira `ceil(500 * V / 4)` por fatia (`:2725`). A soma dos 4 pisos é >= 500 * V, então com as 4 fatias rodando o piso total não cai, e cada fatia passa a ter piso próprio (mais rígido por parte). A ressalva é A2: o argumento vale só se as 4 rodam.
- Nenhuma referência ao nome antigo: `test_fixtures` e `test_t1_variantes_...` não aparecem em `tests/config.json`, `scripts/`, `.github/` nem `.githooks/`; em `tests/pesos-d4.json` só as duas chaves antigas saíram, e as 8 novas entraram (maior peso 195,2 s, abaixo de 225 s).
- Execução local: os 2 testes de cobertura passaram (4,8 s), as 4 fatias do T1 passaram (174,5 s), e `test_pesos_teto` e `test_pesos_do_ci` passaram (18 testes). As fatias de fixtures e a suíte inteira ficam para o CI do PR. Não há run de CI neste head (sem PR, como diz o brief).

## Detalhe dos achados
- A1: evidência em `tests/test_hooks.py:2685` contra `:2704`. Não há caminho de ataque hoje: no head as duas expressões são iguais. O risco é de regressão, porque uma edição futura do fatiamento escapa ao teste que existe para pegá-la. Severidade baixa. Correção mínima: um método `corpus_da_fatia(k)` usado por `verificar_t1_da_fatia` e pelo teste de cobertura. Esforço P. Dono: o autor de E102.4.
- A2: evidência em `tests/test_hooks.py:190-191` e nos métodos `:755-765` e `:2670-2680`. Não há caminho de ataque hoje: são 4 constantes e 4 métodos. O risco é uma mudança de manutenção (mais fatias, ou um método apagado no reequilíbrio) que tira 1/N das fixtures de hook ou do corpus do T1, sem nenhum teste vermelho. Isso enfraqueceria a guarda de conformidade em silêncio. Severidade baixa. Correção mínima: no teste de cobertura, `hasattr(self, f"test_fixtures_fatia_{k+1}")` para cada k em `range(FATIAS_DE_FIXTURES)`, e o mesmo com `test_t1_fatia_{k+1}_variantes_que_o_bash_ignora_nao_tiram_comando_da_leitura` em `range(FATIAS_DO_T1)`. Esforço P. Dono: o autor de E102.4.

## Riscos aceitos e ferramentas
Sem risco aceito. Revisão estática do diff e execução local dos testes novos e das fatias do T1. Nenhuma varredura de segredo ou de dependência: o diff não tem credencial nem dependência.
