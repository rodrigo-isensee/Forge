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
Erro interno: libera e vai ao erros.log.
"""
import datetime
import json
import os
import re
import subprocess
from pathlib import Path

from _comum import PLUGIN, bloquear, caminhos_extra, e_clone_do_forge, executar, expandir_home, gravar_json, ler_json

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


def ultima_mensagem(transcrito, papel="assistant"):
    """O texto da última mensagem de `papel` (com texto; a do dono é `user`) no transcrito JSONL, lido do fim (até
    LEITURA_MAXIMA bytes). Conteúdo em texto puro vale como um bloco de texto."""
    try:
        with open(transcrito, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - LEITURA_MAXIMA))
            linhas = f.read().decode("utf-8", errors="replace").splitlines()
    except (OSError, TypeError, ValueError):
        return None
    for linha in reversed(linhas):
        try:
            obj = json.loads(linha)
            conteudo = obj["message"]["content"]
            blocos = [{"type": "text", "text": conteudo}] if isinstance(conteudo, str) else conteudo
            textos = [c["text"] for c in blocos if c["type"] == "text"] if obj["type"] == papel else []
        except (ValueError, KeyError, TypeError, AttributeError):
            continue
        if textos:
            return "\n".join(textos)
    return None


# Classes de jargão (diretriz 31; desenho em docs/arquitetura/visao-de-foco.md, seção 5.3): fonte única das expressões.
CLASSES_DE_JARGAO = {
    "etapa": re.compile(r"(?<![\w.])E\d+\.\d+(?!\w|\.\w)"),
    "commit": re.compile(r"(?<![\w-])(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}(?![\w-])"),
    "regra": re.compile(r"(?<![\w-])R-[A-Z]{3,}(?![\w-])"),
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


# MP1 (diretriz 35): o sinal de vários projetos ativos é o arquivo ATIVOS, {"projetos": ["<nome>", ...]}, que o registro da
# máquina (MP2, 0.47.6) vai preencher; aqui só se lê. O nome do projeto é o da pasta da raiz.
ATIVOS = "~/.forge/maquina/projetos-ativos.json"
PREFIXO_DO_PROJETO = re.compile(r"\s*Projeto: \S")
PERGUNTA_DO_PROJETO = "isto é para o projeto"


def projetos_ativos():
    """Os nomes de ATIVOS; [] sem o arquivo, ilegível ou fora da forma (conta como um projeto só: nada muda)."""
    try:
        dados = ler_json(Path(expandir_home(ATIVOS)), {})
    except (OSError, ValueError):
        return []
    lista = dados.get("projetos") if isinstance(dados, dict) else None
    return [n for n in lista if isinstance(n, str) and n.strip()] if isinstance(lista, list) else []


def medida_do_projeto(hook, raiz, texto):
    """MP1: {} com um projeto ativo, sem raiz ou na sessão do próprio Forge (exceção do dono, 17/11); senão as contagens."""
    ativos = projetos_ativos()
    if len(ativos) < 2 or raiz is None or e_clone_do_forge(raiz):
        return {}
    fala = ultima_mensagem(hook.campo("transcript_path"), "user") or ""
    outros = [n for n in ativos if n != Path(raiz).name]
    cita = any(re.search(r"(?<![\w-])" + re.escape(n) + r"(?![\w-])", fala, re.I) for n in outros)
    return {"projetos_ativos": len(ativos), "sem_projeto": not PREFIXO_DO_PROJETO.match(texto), "cita_outro_projeto": cita,
            "sem_pergunta_do_projeto": cita and PERGUNTA_DO_PROJETO not in texto.lower()}


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
        achados = sorted({p for p in jargao() if re.search(r"(?<!\w)" + re.escape(p) + r"(?!\w)", medido, re.I)})
        linha = {"em": agora(), "caracteres": len(texto), "teto": TETO_DA_MENSAGEM, "passou_do_teto": len(texto) > TETO_DA_MENSAGEM,
                 "jargao": achados, "classes": classes_de_jargao(medido), "cortado": len(texto) > TETO_DA_MEDIDA,
                 "idioma": idioma, "idioma_do_dono": dono,
                 "outro_idioma": idioma is not None and dono is not None and idioma != dono, "iniciante": hook.iniciante(),
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
