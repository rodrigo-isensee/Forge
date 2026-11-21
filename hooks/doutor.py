#!/usr/bin/env python3
"""Forge: doutor (primeiro uso, F3) - roda as conferências rápidas do `forge doutor` ao abrir a sessão e uma vez por dia.

SessionStart: faz o diagnóstico rápido (local, sem rede, sem `gh`) e grava em `.forge/run/doutor`
`{"data", "problemas", "avisado"}`; nunca escreve no stdout (nele o SessionStart vira contexto do modelo, ADR 0003).
Antes, no SessionStart, soma as pastas de `caminhos_extra` ao fim do PATH da sessão pelo `CLAUDE_ENV_FILE` (E18.1, `caminhos_na_sessao`).
Stop: se a data do cache não é a de hoje, refaz o diagnóstico (uma vez por dia); se há problema ainda não avisado,
imprime só `{"systemMessage": "Forge doutor: ..."}` (uma linha, para o USUÁRIO, nunca `additionalContext`) e marca
como avisado. Também no Stop, uma vez por dia (consulta que falha não marca o dia), consulta as releases do Forge (`git ls-remote --tags`, 3 s, só https; cache em
`.forge/run/versao-nova`) e acrescenta à mesma linha o aviso de versão nova e, também uma vez por dia, o do relógio (desvio de mais de 300 s contra o `Date` do GitHub, só se a consulta de versão deu certo).
No Stop, também os avisos do FORGE-SEMPRE-ATUAL (ADR 0017), lidos do estado da ferramenta: o pendente (volta, fixação) uma vez, e o
adiamento repetido uma vez por contagem. E o aviso de versão parada (v0478 E69.3): 2 dias ou mais atrás da última versão vista,
um por dia, com a causa e o comando que a pessoa roda; medida em `.forge/run/versao-parada.log`. Tudo em ordem: silêncio. Só avisa: o conserto é do comando `forge doutor`, num terminal, com "s".
Erro interno: sai 0 e registra em `erros.log`. Só biblioteca padrão."""
import datetime
import json
import os
import re
import shlex
import stat
import sys
import time
from pathlib import Path

from _comum import PLUGIN, caminhos_extra, executar, forge_doutor, gravar_json, ler_json

LIMITE_LINHA = 200


def hoje():
    return os.environ.get("FORGE_HOJE") or time.strftime("%Y-%m-%d")  # FORGE_HOJE: só os testes


LIMITE_GIT = 3  # segundos por comando `git` do diagnóstico (o padrão do comando é 15)
ESPERA_APOS_FALHA = 600  # segundos sem nova tentativa depois de uma consulta que falhou (não custa 3 s por turno sem rede)
LIMITE_REDE = 3  # segundos da consulta diária às releases do Forge (a única parte que usa a rede, só no Stop)
# Estado do FORGE-SEMPRE-ATUAL: caminho fixo, nunca derivado de CLAUDE_PLUGIN_DATA (ADR 0017, seção 5.1 do desenho).
ESTADO_SEMPRE_ATUAL = (".claude", "plugins", "data", "forge-forge", "forge", "sempre-atual")
LIMITE_ESTADO = 1024 * 1024
ADIADO_AVISA_A_PARTIR_DE = 2  # um adiamento só é a regra funcionando; o repetido não fica mudo (seção 3)
PARADO_AVISA_A_PARTIR_DE = 2  # dias atrás da versão vista: um dia de sessão viva é normal; constante, o projeto não desliga (E69.3)
NOME_DO_ESCOPO = {"user": "usuário", "project": "projeto", "local": "local"}


def ler_cache(hook):
    try:
        estado = ler_json(hook.run() / "doutor", {})
    except ValueError:
        return {}
    return estado if isinstance(estado, dict) else {}


def diagnosticar(raiz):
    """O diagnóstico em si, FORA da trava (o `git` pode demorar)."""
    modulo = forge_doutor()
    modulo.LIMITE_GIT = LIMITE_GIT
    return [p.texto for p in modulo.diagnosticar(raiz, rapido=True)]


def registrar(hook, problemas, avisar):
    """Sob a trava: relê o cache, decide se avisa e grava, tudo de uma vez (duas sessões não avisam duas vezes).
    Devolve os problemas a mostrar ao usuário, ou None."""
    with hook.trava():
        antigo = ler_cache(hook)
        igual = antigo.get("data") == hoje() and antigo.get("problemas") == problemas
        avisado = bool(igual and antigo.get("avisado"))
        avisa = avisar and bool(problemas) and not avisado
        gravar_json(hook.run() / "doutor", {"data": hoje(), "problemas": problemas, "avisado": avisado or avisa})
    return problemas if avisa else None


def ler_cache_versao(hook):
    try:
        estado = ler_json(hook.run() / "versao-nova", {})
    except ValueError:
        return {}
    return estado if isinstance(estado, dict) else {}


def superficie_de(raiz):
    """`forge` se a raiz é o clone do Forge (a sessão de quem edita a fábrica), `projeto` nos demais: muda onde a versão nova entra."""
    try:
        nome = json.loads((raiz / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("name")
    except (OSError, ValueError, AttributeError):
        nome = None
    return "forge" if nome == "forge" else "projeto"


def aviso_de_versao_nova(hook, superficie="projeto"):
    """Uma consulta por dia (cache `.forge/run/versao-nova`), FORA da trava; devolve a frase de aviso se saiu versão nova que ainda
    não foi dita (uma vez por versão, não por dia: o mesmo par `atual`/`ultima` já avisado em outro dia fica em silêncio); senão
    None. Consulta desligada ou em dia: silêncio e o dia fica marcado. Consulta que
    FALHA (sem rede) não marca o dia: tenta de novo daqui a `ESPERA_APOS_FALHA` s. O cache também diz, para o `forge-check`, se o
    plugin está atrás (`defasado`, com `atual` e `ultima`)."""
    agora = time.time()
    with hook.trava():
        antigo = ler_cache_versao(hook)
        if antigo.get("data") == hoje():
            texto, avisa = str(antigo.get("texto") or ""), bool(antigo.get("texto")) and not antigo.get("avisado")
            if avisa:
                gravar_json(hook.run() / "versao-nova", {**antigo, "avisado": True})
            return texto if avisa else None
        falhou_em = antigo.get("falhou_em")
        if isinstance(falhou_em, (int, float)) and 0 <= agora - falhou_em < ESPERA_APOS_FALHA:
            return None
    sys.path.insert(0, str(PLUGIN / "bin"))
    import forge_versoes
    resultado = forge_versoes.consultar_versao(LIMITE_REDE)
    with hook.trava():  # outra sessão pode ter consultado enquanto esta esperava a rede
        antigo = ler_cache_versao(hook)
        if resultado["estado"] == "falhou":
            if antigo.get("data") != hoje():
                gravar_json(hook.run() / "versao-nova", {**antigo, "falhou_em": agora})  # sem `data` de hoje: o dia não fica marcado
            return None
        if antigo.get("data") == hoje():
            texto, avisado = str(antigo.get("texto") or ""), bool(antigo.get("avisado"))
        else:
            defasada = resultado["estado"] == "defasada"
            texto = forge_versoes.texto_de_versao_nova(resultado["atual"], resultado["ultima"], superficie) if defasada else ""
            avisado = defasada and antigo.get("avisado") is True and (antigo.get("atual"), antigo.get("ultima")) == (
                resultado["atual"], resultado["ultima"])  # a mesma versão nova já dita num dia anterior não volta amanhã
        avisa = bool(texto) and not avisado
        novo = antigo if antigo.get("data") == hoje() else {
            "data": hoje(), "texto": texto, "defasado": resultado["estado"] == "defasada",
            "atual": resultado["atual"], "ultima": resultado["ultima"]}
        if novo is not antigo and resultado["estado"] == "desligada":
            novo["consulta"] = "desligada"  # o `forge-check` diz `versão não conferida`, não fica mudo
            if antigo.get("defasado") is True and antigo.get("atual") == resultado["atual"]:
                novo.update(defasado=True, ultima=antigo.get("ultima", ""))  # consulta desligada não apaga uma prova de atraso
        gravar_json(hook.run() / "versao-nova", {**novo, "avisado": avisado or avisa})
    return texto if avisa else None


def aviso_de_relogio(hook):
    """Uma vez por dia, no mesmo cache `versao-nova` (chave `relogio`): confere o relógio contra o `Date` do GitHub, FORA da trava, e devolve
    a frase se o desvio passa de 300 s e ainda não foi dita hoje. Só roda se a consulta de versão do dia deu certo (e não está desligada).
    Consulta que falha não marca o dia: tenta de novo daqui a `ESPERA_APOS_FALHA` s. O desvio nunca é gravado, só a frase."""
    agora = time.time()
    with hook.trava():
        antigo = ler_cache_versao(hook)
        if antigo.get("data") != hoje() or antigo.get("consulta") == "desligada":
            return None
        registro = antigo.get("relogio")
        if isinstance(registro, dict) and registro.get("data") == hoje():
            texto, avisa = str(registro.get("texto") or ""), bool(registro.get("texto")) and not registro.get("avisado")
            if avisa:
                gravar_json(hook.run() / "versao-nova", {**antigo, "relogio": {**registro, "avisado": True}})
            return texto if avisa else None
        falhou_em = antigo.get("relogio_falhou_em")
        if isinstance(falhou_em, (int, float)) and 0 <= agora - falhou_em < ESPERA_APOS_FALHA:
            return None
    sys.path.insert(0, str(PLUGIN / "bin"))
    import forge_versoes
    desvio = forge_versoes.desvio_do_relogio(forge_versoes.url_do_forge(), LIMITE_REDE)
    with hook.trava():
        antigo = ler_cache_versao(hook)
        if desvio is None:
            if not (isinstance(antigo.get("relogio"), dict) and antigo["relogio"].get("data") == hoje()):
                gravar_json(hook.run() / "versao-nova", {**antigo, "relogio_falhou_em": agora})  # sem `relogio` de hoje: o dia não fica marcado
            return None
        texto = forge_versoes.texto_de_relogio(desvio)
        novo = {k: v for k, v in antigo.items() if k != "relogio_falhou_em"}
        novo["relogio"] = {"data": hoje(), "texto": texto, "avisado": bool(texto)}
        gravar_json(hook.run() / "versao-nova", novo)
    return texto or None


def frases_do_sempre_atual(estado):
    """As frases ainda não ditas do estado da ferramenta, marcando-as no próprio `estado` (o chamador grava). Devolve (frases, mudou)."""
    frases = []
    aviso = estado.get("aviso")
    if isinstance(aviso, dict) and isinstance(aviso.get("texto"), str) and aviso["texto"].strip() and not aviso.get("avisado"):
        frases.append("Forge: " + " ".join(aviso["texto"].split()))
        aviso["avisado"] = True
    adiamentos = estado.get("adiamentos")
    for escopo, reg in sorted(adiamentos.items()) if isinstance(adiamentos, dict) else ():
        n = reg.get("n") if isinstance(reg, dict) else None
        if not isinstance(n, int) or isinstance(n, bool) or n < ADIADO_AVISA_A_PARTIR_DE or reg.get("avisado") == n:
            continue
        desde = " ".join(str(reg.get("desde", "?")).split())[:32]
        frases.append(f"Forge adiado {n} vezes desde {desde} (trabalho em curso; escopo {NOME_DO_ESCOPO.get(escopo, '?')})")
        reg["avisado"] = n
    return frases, bool(frases)


def pasta_do_sempre_atual():
    """A pasta de estado da ferramenta (o HOME do ambiente, como ela), ou None se falta ou não é própria (link, outro dono)."""
    pasta = Path.home().joinpath(*ESTADO_SEMPRE_ATUAL)
    try:
        st = os.lstat(pasta)
    except OSError:
        return None
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid():
        return None
    return pasta


def causa_da_parada(fv, raiz, carregada):
    """(causa, extra), só por leitura: a sessão atrás da instalada; senão a última linha do registro da ferramenta que falhou;
    senão o adiamento; senão a abertura sem o atalho (também quando nada é legível, R2 do desenho)."""
    instalada = fv.versao_instalada(Path.home(), raiz)
    if instalada and fv.versao_de(instalada) > fv.versao_de(carregada):
        return "sessao-antiga", instalada
    pasta = pasta_do_sempre_atual()
    if pasta is None:
        return "sem-atalho", ""
    registro = (fv._ler_limitado(pasta / "registro.log", 4 * LIMITE_ESTADO) or "").strip().splitlines()
    resultado = registro[-1].split("\t")[-1].split(":") if registro else [""]
    if resultado[0] == "falhou":
        etapa = resultado[1] if len(resultado) > 1 else ""
        return "falhou", etapa if re.fullmatch(r"[a-z0-9-]{1,32}", etapa) else "?"
    try:
        estado = json.loads(fv._ler_limitado(pasta / "estado.json", LIMITE_ESTADO) or "{}")
    except ValueError:
        estado = {}
    adiamentos = estado.get("adiamentos") if isinstance(estado, dict) else None
    vezes = [r["n"] for r in adiamentos.values() if isinstance(r, dict) and type(r.get("n")) is int] if isinstance(adiamentos, dict) else []
    return ("adiada", str(max(vezes))) if vezes and max(vezes) > 0 else ("sem-atalho", "")


def medir(hook, estado, alcancada):
    """Uma linha `versao · vista_em · avisada_em · causa · alcancada_em` em `.forge/run/versao-parada.log` (só mede, nada decide)."""
    campos = [str(estado.get(c)) for c in ("versao", "vista_em", "avisada_em", "causa")] + [alcancada]
    fd = os.open(hook.run() / "versao-parada.log", os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o644)
    with os.fdopen(fd, "a", encoding="utf-8") as f:
        f.write(" · ".join(campos) + "\n")


def aviso_de_versao_parada(hook, raiz, superficie):
    """A sessão atrás da última versão vista (`ultima` do cache `versao-nova`) há `PARADO_AVISA_A_PARTIR_DE` dias ou mais: uma frase
    por dia, com a causa e o comando, e outra no mesmo dia se a causa mudar. Sem rede vale o `ultima` guardado, com a data dele.
    Estado em `.forge/run/versao-parada` (`versao`, `vista_em`, `avisada_em`, `causa`); a sessão que alcança a versão fecha a medida."""
    sys.path.insert(0, str(PLUGIN / "bin"))
    import forge_versoes as fv
    carregada = fv.versao_do_plugin()
    agora = fv.versao_de(carregada)
    texto = None
    with hook.trava():
        cache = ler_cache_versao(hook)
        try:
            estado = ler_json(hook.run() / "versao-parada", {})
        except ValueError:
            estado = {}
        estado = estado if isinstance(estado, dict) else {}
        novo, vista = dict(estado), fv.versao_de(str(estado.get("versao", "")))
        if vista and agora and agora >= vista:
            if estado.get("avisada_em"):
                medir(hook, estado, hoje())
            novo = {}
        ultima = fv.versao_de(str(cache.get("ultima", "")))
        if ultima and agora and ultima > agora:
            main = ".".join(map(str, ultima))
            if novo.get("versao") != main:
                novo = {"versao": main, "vista_em": hoje()}
            try:
                dias = (datetime.date.fromisoformat(hoje()) - datetime.date.fromisoformat(str(novo.get("vista_em")))).days
            except ValueError:
                novo, dias = {"versao": main, "vista_em": hoje()}, 0
            causa, extra = causa_da_parada(fv, raiz, carregada) if dias >= PARADO_AVISA_A_PARTIR_DE else ("", "")
            if causa and (novo.get("avisada_em"), novo.get("causa")) != (hoje(), causa):
                texto = fv.texto_de_versao_parada(causa, dias, carregada, main, extra, superficie)
                data = str(cache.get("data", ""))
                if data != hoje() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", data):
                    texto += f" (main vista em {data}, sem conferir hoje)"
                novo.update(avisada_em=hoje(), causa=causa)
                medir(hook, novo, "-")
        if novo != estado:
            gravar_json(hook.run() / "versao-parada", novo)
    return texto


def avisos_do_sempre_atual():
    """FORGE-SEMPRE-ATUAL (ADR 0017): lê o `estado.json` da ferramenta e marca o que disse, sob a trava dela (`.trava`, sem esperar).
    Com a ferramenta rodando, ou pasta que não é própria (link, outro dono), fica para o próximo Stop; nunca cria a pasta."""
    import fcntl
    pasta = pasta_do_sempre_atual()
    if pasta is None:
        return []
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(pasta / ".trava", os.O_RDWR | os.O_CREAT | nofollow, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return []
        try:
            with open(os.open(pasta / "estado.json", os.O_RDONLY | nofollow), encoding="utf-8") as f:
                estado = json.loads(f.read(LIMITE_ESTADO + 1))
        except (OSError, ValueError):
            return []
        if not isinstance(estado, dict):
            return []
        frases, mudou = frases_do_sempre_atual(estado)
        if mudou:
            tmp = pasta / f".estado.json.doutor.{os.getpid()}"
            with open(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | nofollow, 0o600), "w", encoding="utf-8") as f:
                json.dump(estado, f, ensure_ascii=False, indent=2)
            os.replace(tmp, pasta / "estado.json")
        return frases
    finally:
        os.close(fd)


def caminhos_na_sessao(hook, raiz):
    """E18.1 (0.45.7): as pastas de `caminhos_extra` (.forge/config.json) vão ao fim do PATH dos comandos do Bash da sessão, pelo
    arquivo de ambiente que o Claude Code dá ao SessionStart (`CLAUDE_ENV_FILE`), com a conferência do `_comum.caminhos_extra`; a
    pasta que não passa fica de fora, com aviso no erros.log. Sem o arquivo ou sem pasta boa, nada muda; a mesma linha não se repete
    (resume e compact)."""
    destino = os.environ.get("CLAUDE_ENV_FILE")
    if not destino:
        return
    pastas, avisos = caminhos_extra(raiz)
    for aviso in avisos:
        hook.registrar_escape(aviso)
    if not pastas:
        return
    texto = 'export PATH="$PATH"' + "".join(":" + shlex.quote(p) for p in pastas) + "\n"
    try:
        with open(destino, encoding="utf-8") as f:
            antes = f.read()
    except FileNotFoundError:
        antes = ""
    if texto in antes.splitlines(keepends=True):
        return
    separador = "\n" if antes and not antes.endswith("\n") else ""
    with open(destino, "a", encoding="utf-8") as f:
        f.write(separador + texto)


def linha(problemas):
    n = len(problemas)
    primeiro = " ".join(problemas[0].split())
    texto = f"Forge doutor: {n} {'coisa' if n == 1 else 'coisas'} para ver — {primeiro}"
    cauda = " (rode: forge doutor)"
    return texto[: LIMITE_LINHA - len(cauda) - 1] + "…" + cauda if len(texto) + len(cauda) > LIMITE_LINHA else texto + cauda


def preparar_controle(hook):
    """SANDBOX-TRAVA-CONTROLE (A2 da segurança): `agentes.json` e `pesado.json` negados ao Bash existem antes do primeiro comando
    da sessão. Ausente, o runtime do sandbox o criaria vazio e 0444 no disco. Só cria o que falta, nunca regrava o que existe."""
    run = hook.run()
    for nome, conteudo in (("agentes.json", {"agentes": []}), ("pesado.json", None)):
        if not os.path.lexists(run / nome):
            gravar_json(run / nome, conteudo)


def principal(hook):
    evento = hook.campo("hook_event_name")
    if evento not in ("SessionStart", "Stop"):
        return
    raiz = hook.projeto(hook.cwd())
    if raiz is None:
        return
    if evento == "SessionStart":  # inclusive resume e compact: reexamina sem reabrir o aviso de hoje
        caminhos_na_sessao(hook, raiz)
        try:
            preparar_controle(hook)
        except OSError as erro:  # o aviso do doutor não cai por isso; o erro vai ao erros.log
            hook.registrar_erro(erro)
        registrar(hook, diagnosticar(raiz), avisar=False)
        return
    with hook.trava():  # cache de hoje: decide e marca "avisado" na mesma trava
        estado = ler_cache(hook)
        valido = estado.get("data") == hoje() and isinstance(estado.get("problemas"), list)
        problemas = [str(p) for p in estado["problemas"]] if valido else []
        avisa = valido and bool(problemas) and not estado.get("avisado")
        if avisa:
            estado["avisado"] = True
            gravar_json(hook.run() / "doutor", estado)
    mostrar = problemas if avisa else None
    if not valido:  # primeira vez hoje: diagnostica fora da trava e decide de novo, relendo o cache
        mostrar = registrar(hook, diagnosticar(raiz), avisar=True)
    partes = [linha(mostrar)] if mostrar else []
    try:
        partes += avisos_do_sempre_atual()
    except OSError as erro:  # a falha ao ler ou gravar o estado da ferramenta não come os outros avisos
        hook.registrar_erro(erro)
    nova = aviso_de_versao_nova(hook, superficie_de(raiz))
    if nova:
        partes.append(nova)
    try:
        parada = aviso_de_versao_parada(hook, raiz, superficie_de(raiz))
    except OSError as erro:  # a falha ao ler ou medir não come o aviso de versão nem o do relógio
        hook.registrar_erro(erro)
        parada = None
    if parada:
        partes.append(parada)
    try:
        relogio = aviso_de_relogio(hook)
    except OSError:  # a falha ao gravar o relógio não pode comer o aviso de versão, que já está marcado como dito
        relogio = None
    if relogio:
        partes.append(relogio)
    if partes:
        print(json.dumps({"systemMessage": " · ".join(partes)}, ensure_ascii=False))


if __name__ == "__main__":
    executar("doutor", principal)
    sys.exit(0)
