#!/usr/bin/env python3
"""Forge: objetivo armado no Stop (S4) e medida da mensagem ao dono (S6), 0.44.2. Só biblioteca padrão.

Stop, com objetivo armado (`forge-check meta --armar <pedido> --checagem "<cmd>"...`, estado em .forge/run/meta.json):
- **espera o dono**: o pedido está em `## Aguardando o dono` do KANBAN.md ou a última linha do dono no pedido é uma
  `PERGUNTA AO DONO` sem `DECISÃO DO DONO` depois; o Stop passa e o objetivo fica armado.
- **entregue e provado**: toda checagem (sem shell, até CHECAGEM_S cada) sai com rc 0; o Stop passa e o objetivo se desarma.
- **ainda não**: bloqueia o Stop dizendo as checagens que falharam. REPETICOES_PARA_PAUSAR "ainda não" iguais seguidos
  pausam o objetivo sozinho (o Stop passa, `pausado` no meta.json): não fica em laço.
Sem objetivo armado, nada muda. S6: em todo Stop, só MEDE (nunca bloqueia) a última mensagem ao dono (o campo
last_assistant_message do evento; sem ele, o transcrito): caracteres contra TETO_DA_MENSAGEM, as palavras da tabela "Em vez de"
de skills/modo-iniciante/SKILL.md e, por classe de CLASSES_DE_JARGAO (diretriz 31), quantos termos sem explicação há fora de
bloco de código e de citação; grava uma linha em .forge/run/mensagens.jsonl (só contagens e as palavras da tabela, nunca o
texto nem o termo achado das classes). SIEG-G4 (0.47.4): a linha leva também o idioma da mensagem (por palavras
frequentes de PALAVRAS_DO_IDIOMA, fora de código e citação) e `outro_idioma`, verdadeiro quando ele difere do idioma do dono
(`idioma_do_dono` no .forge/config.json do projeto; ausente: IDIOMA_PADRAO; código sem lista: sem medida). A medida roda depois da decisão do objetivo e lê só TETO_DA_MEDIDA caracteres
(`cortado` na linha): o tempo dela não cresce com a mensagem. MP1 (diretriz 35, 0.47.5): com mais de um projeto ativo
(nomes em ATIVOS), fora da sessão do próprio Forge, a linha leva também se a mensagem não começa por `Projeto:` e se a
última fala do dono cita outro projeto ativo sem a pergunta "isto é para o projeto" (só contagens, nunca o nome).
E25.1 (0.47.9): o idioma vale também para as notas entre chamadas de ferramenta da rodada (desde a última fala do dono,
do transcrito, até TETO_DA_MEDIDA caracteres): `notas_em_outro_idioma` conta as que diferem, e `outro_idioma` as inclui.
E109.1: num segundo Stop sem fala nova do dono, a rodada para no registro mais novo já lido e pula a final anterior
(MARCA_DAS_NOTAS, só o uuid e o sha256, nunca o texto): nada se reconta. E137.1: uma marca por transcrito (até
MARCAS_GUARDADAS), pois o .forge/run é um só para as sessões do projeto.
Erro interno: libera e vai ao erros.log.
"""
import datetime
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from _comum import (ARQUIVO_DE_ATIVOS, MAXIMO_DE_ATIVOS, MAXIMO_DO_NOME, PLUGIN, TETO_DE_ATIVOS, bloquear, caminhos_extra,
                    e_clone_do_forge, executar, gravar_json, ler_json, ler_projetos_ativos)
from vigia import texto_do_dono

CHECAGEM_S = 60
REPETICOES_PARA_PAUSAR = 4
TETO_DA_MENSAGEM = 1200  # caracteres da mensagem ao dono (S6, só medida)
LEITURA_MAXIMA = 4 * 1024 * 1024  # bytes lidos do fim do transcrito
TETO_DA_MEDIDA = 20000  # caracteres do início da mensagem que a medida lê (S6): o tempo dela não cresce com a mensagem
JANELA_DA_FRASE = 200  # caracteres antes do termo onde explicado() procura o "o que é" da mesma frase


def agora():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def secao(texto, titulo):
    m = re.search(r"^## " + re.escape(titulo) + r"\s*$(.*?)(?=^## |\Z)", texto, re.M | re.S)
    return m.group(1) if m else ""


def ler(caminho):
    try:
        return Path(caminho).read_text(encoding="utf-8")
    except (OSError, ValueError):
        return ""


def espera_o_dono(raiz, pedido):
    """O pedido aguarda o dono: no painel do KANBAN.md ou com PERGUNTA AO DONO sem DECISÃO DO DONO depois."""
    if re.search(r"(?<![\w/.-])" + re.escape(pedido) + r"(?![\w/.-])", secao(ler(raiz / "KANBAN.md"), "Aguardando o dono")):
        return True
    linhas = [l for l in ler(raiz / "docs" / "pedidos" / f"{pedido}.md").splitlines() if re.match(r"\s*(?:- )?(PERGUNTA AO|DECISÃO DO) DONO", l)]
    return bool(linhas) and "PERGUNTA AO DONO" in linhas[-1]


def ambiente_das_checagens(hook, raiz):
    """0.45.4: o ambiente do hook com as pastas de `caminhos_extra` (.forge/config.json) no fim do PATH, como o
    `.githooks/pre-push`: a checagem acha a ferramenta da stack mesmo quando o agente abre sem o PATH do terminal. A pasta que
    não passa na conferência fica de fora, com aviso no erros.log."""
    pastas, avisos = caminhos_extra(raiz)
    for aviso in avisos:
        hook.registrar_escape(aviso)
    ambiente = dict(os.environ)
    if pastas:
        ambiente["PATH"] = os.pathsep.join(filter(None, [ambiente.get("PATH", ""), *pastas]))
    return ambiente


def falhas(raiz, checagens, ambiente=None):
    """As checagens (argv) que não saíram com rc 0, como texto. `ambiente`: o do processo (com o PATH dos `caminhos_extra`)."""
    saida = []
    for argv in checagens:
        try:
            rc = subprocess.run(argv, cwd=raiz, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                timeout=CHECAGEM_S, env=ambiente).returncode
        except (OSError, subprocess.TimeoutExpired):
            rc = "erro"
        if rc != 0:
            saida.append(f"`{' '.join(argv)[:80]}` (rc={rc})")
    return saida


def avaliar_meta(hook, raiz):
    arquivo = hook.run() / "meta.json"
    meta = ler_json(arquivo, None)
    if not isinstance(meta, dict) or not meta.get("armado") or meta.get("pausado"):
        return
    pedido, checagens = str(meta.get("pedido", "")), [c for c in meta.get("checagens", []) if isinstance(c, list) and c]
    if espera_o_dono(raiz, pedido):
        gravar_json(arquivo, {**meta, "estado": "espera o dono", "repeticoes": 0, "ultimo": None, "em": agora()})
        return
    falhou = falhas(raiz, checagens, ambiente_das_checagens(hook, raiz))
    if not falhou:
        gravar_json(arquivo, {**meta, "armado": False, "estado": "entregue e provado", "repeticoes": 0, "em": agora()})
        return
    repeticoes = meta.get("repeticoes", 0) + 1 if meta.get("ultimo") == falhou else 1
    if repeticoes >= REPETICOES_PARA_PAUSAR:
        gravar_json(arquivo, {**meta, "pausado": True, "estado": "pausado", "repeticoes": repeticoes, "ultimo": falhou, "em": agora()})
        return
    gravar_json(arquivo, {**meta, "estado": "ainda não", "repeticoes": repeticoes, "ultimo": falhou, "em": agora()})
    bloquear("R-PROVA", f"objetivo do pedido {pedido} ainda não entregue ({repeticoes}/{REPETICOES_PARA_PAUSAR}): falharam "
                        + "; ".join(falhou) + ". Corrija e pare de novo; se espera o dono, registre a PERGUNTA AO DONO.")


# ---- S6: medida da mensagem ao dono ----
TABELA = re.compile(r"^\|\s*Em vez de\s*\|.*\n\|[-|: ]+\|\n((?:[ \t]*\|.*\n)+)", re.M)


def jargao():
    """As palavras da coluna "Em vez de" da tabela de skills/modo-iniciante/SKILL.md (fonte única); [] sem a tabela."""
    try:
        linhas = TABELA.search(ler(PLUGIN / "skills" / "modo-iniciante" / "SKILL.md").replace("  |", "|")).group(1).splitlines()
    except AttributeError:
        return []
    return [p.strip() for linha in linhas for p in linha.strip().strip("|").split("|")[0].split(",")]


def linhas_do_fim(transcrito):
    """As linhas do fim do transcrito JSONL (até LEITURA_MAXIMA bytes), da última à primeira; [] se não se lê."""
    try:
        with open(transcrito, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - LEITURA_MAXIMA))
            return list(reversed(f.read().decode("utf-8", errors="replace").splitlines()))
    except (OSError, TypeError, ValueError):
        return []


def ultima_mensagem(transcrito):
    """O texto da última mensagem do assistente (com texto) no transcrito JSONL, lido do fim (até LEITURA_MAXIMA bytes)."""
    for linha in linhas_do_fim(transcrito):
        try:
            obj = json.loads(linha)
            textos = [c["text"] for c in obj["message"]["content"] if c["type"] == "text"] if obj["type"] == "assistant" else []
        except (ValueError, KeyError, TypeError, AttributeError):
            continue
        if textos:
            return "\n".join(textos)
    return None


def fala_do_dono(transcrito):
    """A última fala digitada pelo dono no transcrito, pelo filtro de vigia.texto_do_dono (fonte única: aviso de subagente,
    meta e lembrete do sistema não contam); None sem ela."""
    for linha in linhas_do_fim(transcrito):
        try:
            texto = texto_do_dono(json.loads(linha))
        except (ValueError, RecursionError):
            continue
        if texto and texto.strip():
            return texto
    return None


# Classes de jargão (diretriz 31; desenho em docs/arquitetura/visao-de-foco.md, seção 5.3): fonte única das expressões.
CLASSES_DE_JARGAO = {
    "etapa": re.compile(r"(?<![\w.])E\d+\.\d+(?!\w|\.\w)"),
    "commit": re.compile(r"(?<![\w-])(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}(?![\w-])"),
    "regra": re.compile(r"(?<![\w-])R-[A-Z]{2,}(?![\w-])"),
    "cartao": re.compile(r"(?<![\w-])[A-Z]{2}[A-Z0-9]*(?:-[A-Z0-9]+)+(?![\w-])"),
    "ferramenta": re.compile(r"(?<![\w/-])(?:forge-[a-z][\w-]*|(?:gh|git) [a-z][\w-]*)|(?:^|(?<=`))forge [a-z][\w-]*", re.M),
    "caminho": re.compile(r"(?<![\w/.-])[\w.-]*/[\w./-]*\.(?:md|py|json|sh)(?![\w-])"),
}
EXPLICACAO = re.compile(r"[^\n(.!?]{0,60}\(\s*[^)\s]")  # parêntese com texto em até 60 caracteres, na mesma frase


def fora_de_codigo_e_citacao(texto):
    """As linhas da mensagem fora de bloco de código cercado (``` ou ~~~, fechado pela mesma cerca) e de citação (>):
    o que entra na conta das classes."""
    linhas, cerca = [], None
    for linha in texto.splitlines():
        inicio = linha.lstrip()[:3]
        if cerca is None and inicio in ("```", "~~~"):
            cerca = inicio
        elif cerca is not None:
            cerca = None if inicio == cerca else cerca
        elif not inicio.startswith(">"):
            linhas.append(linha)
    return "\n".join(linhas)


def explicado(texto, inicio, fim):
    """O termo vem seguido de parêntese com texto (até 60 caracteres) ou precedido de "o que é" na mesma frase, procurado
    só na janela antes do termo: o custo não cresce com o tamanho da mensagem."""
    frase = re.split(r"[.!?\n]", texto[max(0, inicio - JANELA_DA_FRASE):inicio])[-1]
    return bool(EXPLICACAO.match(texto, fim)) or "o que é" in frase.lower()


def classes_de_jargao(texto):
    """Por classe, quantos termos sem explicação; só as classes achadas (nunca o termo)."""
    texto = fora_de_codigo_e_citacao(texto)
    contagem = {nome: sum(not explicado(texto, m.start(), m.end()) for m in padrao.finditer(texto))
                for nome, padrao in CLASSES_DE_JARGAO.items()}
    return {nome: n for nome, n in contagem.items() if n}


# SIEG-G4: idioma da mensagem ao dono. Listas disjuntas de palavras frequentes; o idioma com mais ocorrências, desde que
# chegue a MINIMO_DO_IDIOMA e não empate: mensagem curta ou mista fica sem idioma (None) e não é acusada.
IDIOMA_PADRAO = "pt"
MINIMO_DO_IDIOMA = 3
PALAVRAS_DO_IDIOMA = {
    "pt": frozenset("não que uma um os na no do da em é está são você isso também mas então ainda já muito".split()),
    "en": frozenset("the and is are of to that this with for you it not was have will be but on what".split()),
    "es": frozenset("el los las es del pero con usted esto también muy bien cuando hay".split()),
}


def idioma_da_mensagem(texto):
    """O código do idioma de PALAVRAS_DO_IDIOMA com mais palavras no texto; None abaixo de MINIMO_DO_IDIOMA ou com empate."""
    palavras = re.findall(r"[^\W\d_]+", texto.lower())
    contagem = sorted(((sum(p in lista for p in palavras), idioma) for idioma, lista in PALAVRAS_DO_IDIOMA.items()), reverse=True)
    (maior, idioma), (segundo, _) = contagem[0], contagem[1]
    if maior < MINIMO_DO_IDIOMA or maior == segundo:
        return None
    return idioma


def idioma_do_dono(raiz):
    """`idioma_do_dono` do .forge/config.json da raiz (neutro: vem do projeto); sem raiz, arquivo ou chave: IDIOMA_PADRAO.
    Código sem lista em PALAVRAS_DO_IDIOMA: None (sem medida, para não acusar o próprio idioma do dono)."""
    config = ler_json(Path(raiz) / ".forge" / "config.json", {}) if raiz is not None else {}
    valor = config.get("idioma_do_dono") if isinstance(config, dict) else None
    if valor is None:
        return IDIOMA_PADRAO
    return valor if isinstance(valor, str) and valor in PALAVRAS_DO_IDIOMA else None


# MP1 (diretriz 35): o sinal de vários projetos ativos é o arquivo ATIVOS (leitor em `_comum.ler_projetos_ativos`).
ATIVOS = ARQUIVO_DE_ATIVOS
PREFIXO_DO_PROJETO = re.compile(r"\s*Projeto: \S")
PERGUNTA_DO_PROJETO = "isto é para o projeto"


def projetos_ativos():
    """Os nomes de ATIVOS; registro ilegível ou fora da forma conta como um projeto só (nada muda); nome fora da forma
    só fica de fora (modo tolerante)."""
    return ler_projetos_ativos(ATIVOS, tolerante=True) or []


def medida_do_projeto(hook, raiz, texto):
    """MP1: {} sem raiz, na sessão do próprio Forge (exceção do dono, 17/11; ATIVOS nem é lido) ou com um projeto ativo;
    senão as contagens. O nome se compara sem diferença de maiúsculas, e a fala lida é só a do dono, até TETO_DA_MEDIDA."""
    if raiz is None or e_clone_do_forge(raiz):
        return {}
    ativos = projetos_ativos()
    if len(ativos) < 2:
        return {}
    fala = (fala_do_dono(hook.campo("transcript_path")) or "")[:TETO_DA_MEDIDA]
    outros = [n for n in ativos if n.casefold() != Path(raiz).name.casefold()]
    cita = any(re.search(r"(?<![\w-])" + re.escape(n) + r"(?![\w-])", fala, re.I) for n in outros)
    return {"projetos_ativos": len(ativos), "sem_projeto": not PREFIXO_DO_PROJETO.match(texto), "cita_outro_projeto": cita,
            "sem_pergunta_do_projeto": cita and PERGUNTA_DO_PROJETO not in texto.lower()}


MARCA_DAS_NOTAS = "notas.json"  # E109.1: em .forge/run, o que o Stop anterior leu (uuid e sha256 da final, nunca o texto)
MARCAS_GUARDADAS = 8  # E137.1: transcritos com marca própria em MARCA_DAS_NOTAS; o mais velho sai (o arquivo não cresce)


def resumo(texto):
    return hashlib.sha256(texto.strip().encode("utf-8")).hexdigest()


def notas_da_rodada(transcrito, final, marca=None, final_anterior=None):
    """E25.1: os textos do assistente na rodada (desde a última fala do dono), lidos do fim, fora a mensagem `final`, até
    TETO_DA_MEDIDA caracteres somados (o tempo não cresce com a rodada). Subagente (isSidechain) não conta: não fala ao dono.
    E109.1: para também na `marca` (uuid do registro mais novo lido no Stop anterior) e pula o texto cujo resumo é o
    `final_anterior`. Devolve (notas, uuid do registro mais novo lido)."""
    notas, total, final, nova = [], 0, (final or "").strip(), None
    for linha in linhas_do_fim(transcrito):
        if ('"type":"tool_result"' in linha and '"type":"assistant"' not in linha) or (
                '"user"' not in linha and '"assistant"' not in linha):
            continue  # resultado de ferramenta nunca é fala do dono nem nota: nem se decodifica (custo); E137.1: na linha do
            # assistente o input da chamada é objeto (aspas sem escape) e pode trazer o par: ela ainda é nota
        try:
            obj = json.loads(linha)
        except (ValueError, RecursionError):
            continue
        uuid = obj.get("uuid") if isinstance(obj, dict) else None
        if nova is None and isinstance(uuid, str):
            nova = uuid
        if texto_do_dono(obj) or (marca is not None and uuid == marca):
            break
        if not isinstance(obj, dict) or obj.get("type") != "assistant" or obj.get("isSidechain"):
            continue
        conteudo = obj.get("message", {}).get("content") if isinstance(obj.get("message"), dict) else None
        for bloco in conteudo if isinstance(conteudo, list) else []:
            texto = bloco.get("text") if isinstance(bloco, dict) and bloco.get("type") == "text" else None
            if isinstance(texto, str) and texto.strip() and texto.strip() != final and resumo(texto) != final_anterior:
                notas.append(texto[:TETO_DA_MEDIDA - total])
                total += len(notas[-1])
                if total >= TETO_DA_MEDIDA:
                    return notas, nova
    return notas, nova


def vistas_anteriores(arquivo):
    """E109.1 e E137.1: {transcrito: o que o Stop anterior dele leu}, uma marca por sessão (o .forge/run é um só para as
    sessões do projeto); {} sem o arquivo ou ilegível, e a entrada fora da forma fica de fora."""
    try:
        vista = ler_json(arquivo, {})
    except (OSError, ValueError):
        return {}
    return {t: v for t, v in vista.items() if isinstance(v, dict)} if isinstance(vista, dict) else {}


def notas_em_outro_idioma(hook, final, dono):
    """Quantas notas da rodada estão num idioma diferente do `dono` (cada nota medida sozinha; curta ou mista não conta)."""
    if dono is None:
        return 0
    transcrito, arquivo = hook.campo("transcript_path"), hook.run() / MARCA_DAS_NOTAS
    vistas = vistas_anteriores(arquivo)
    vista = vistas.pop(str(transcrito), {})  # sai e volta no fim: a ordem do dict é a do uso mais recente
    notas, marca = notas_da_rodada(transcrito, final, vista.get("marca"), vista.get("final"))
    vistas[str(transcrito)] = {"marca": marca, "final": resumo(final)}
    try:
        gravar_json(arquivo, dict(list(vistas.items())[-MARCAS_GUARDADAS:]))
    except OSError as erro:  # A1 da segurança (E109.7): sem a marca gravada, a contagem e a linha da medida seguem
        hook.registrar_erro(erro)
    return sum(idioma_da_mensagem(fora_de_codigo_e_citacao(n)) not in (None, dono) for n in notas)


def mensagem_ao_dono(hook):
    """A mensagem final do evento (last_assistant_message); o transcrito só sem ela, que ali pode faltar a final (D13)."""
    texto = hook.campo("last_assistant_message")
    if isinstance(texto, str) and texto.strip():
        return texto
    return ultima_mensagem(hook.campo("transcript_path"))


def medir_mensagem(hook, raiz=None):
    for texto in filter(None, [mensagem_ao_dono(hook)]):
        medido = texto[:TETO_DA_MEDIDA]
        idioma, dono = idioma_da_mensagem(fora_de_codigo_e_citacao(medido)), idioma_do_dono(raiz)
        notas = notas_em_outro_idioma(hook, texto, dono)
        achados = sorted({p for p in jargao() if re.search(r"(?<!\w)" + re.escape(p) + r"(?!\w)", medido, re.I)})
        linha = {"em": agora(), "caracteres": len(texto), "teto": TETO_DA_MENSAGEM, "passou_do_teto": len(texto) > TETO_DA_MENSAGEM,
                 "jargao": achados, "classes": classes_de_jargao(medido), "cortado": len(texto) > TETO_DA_MEDIDA,
                 "idioma": idioma, "idioma_do_dono": dono,
                 "notas_em_outro_idioma": notas,
                 "outro_idioma": notas > 0 or (idioma is not None and dono is not None and idioma != dono), "iniciante": hook.iniciante(),
                 **medida_do_projeto(hook, raiz, medido)}
        with open(hook.run() / "mensagens.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")


def principal(hook):
    if hook.campo("hook_event_name") != "Stop":
        return
    raiz = hook.projeto(hook.cwd(), clone_do_forge=True)
    if raiz is None:
        return
    try:
        avaliar_meta(hook, raiz)  # a decisão vem antes da medida; bloquear sai do processo, e a medida roda no finally
    finally:
        try:
            medir_mensagem(hook, raiz)
        except Exception as erro:  # noqa: BLE001 - S6 só mede: a falha da medida nunca troca a decisão do Stop
            hook.registrar_erro(erro)


if __name__ == "__main__":
    executar("meta", principal)
