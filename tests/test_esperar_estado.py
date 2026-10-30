"""PN5-ESPERAR-ESTADO (P-N5): a skill `esperar-estado` espera o PR pelo estado e sai em MERGED ou CLOSED.

O laço do PR é o bloco de código da própria skill, rodado no bash com `gh` e `sleep` falsos no PATH (sem rede, sem
custo). Os blocos passam pelos hooks `parecer` e `conformidade` com o papel `tech-lead`, no clone do Forge e em projeto."""
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_hooks  # noqa: E402
from gh_falso import pasta_com_gh  # noqa: E402
from guarda_git import setUpModule, tearDownModule  # noqa: E402,F401
from test_hooks import Fixture  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SKILL = RAIZ / "skills" / "esperar-estado" / "SKILL.md"
TECH_LEAD = RAIZ / "agents" / "tech-lead.md"
BLOCOS = re.findall(r"```bash\n(.*?)```", SKILL.read_text(encoding="utf-8"), re.S)

# `gh` falso: `pr view` devolve a linha N de `estados` na N-ésima leitura (a última se repete) e anota a leitura;
# `pr checks` sai com o código gravado em `checks`; com o arquivo `falha`, `pr view` sai com 1.
GH = """d=$(dirname "$0")
if [ "$2" = view ]; then
  [ -f "$d/falha" ] && { echo 'gh falso: falhou' >&2; exit 1; }
  echo v >> "$d/vistas"; n=$(wc -l < "$d/vistas")
  e=$(sed -n "${n}p" "$d/estados"); [ -n "$e" ] || e=$(tail -n 1 "$d/estados"); echo "$e"; exit 0
fi
exit "$(cat "$d/checks")"
"""


def laco():
    blocos = [b for b in BLOCOS if "gh pr view" in b]
    assert len(blocos) == 1, "a skill tem um laço do PR só"
    return blocos[0]


def laco_do_log():
    blocos = [b for b in BLOCOS if "'^rc='" in b]
    assert len(blocos) == 1, "a skill tem um laço do log só"
    return blocos[0]


def lancamento():
    linhas = re.findall(r"(?m)^`(<envio> > .*)`$", SKILL.read_text(encoding="utf-8"))
    assert len(linhas) == 1, "a skill tem uma linha de lançamento só"
    return linhas[0]


def com_log(texto, caminho):
    """Troca o marcador `<log>` da skill pelo caminho literal do log, como o agente faz."""
    return texto.replace("<log>", str(caminho))


class LacoDoPr(unittest.TestCase):
    def rodar(self, estados, checks=8, falha=False):
        pasta = pasta_com_gh(GH)
        (pasta / "estados").write_text("\n".join(estados) + "\n", encoding="utf-8")
        (pasta / "checks").write_text(f"{checks}\n", encoding="utf-8")
        if falha:
            (pasta / "falha").write_text("", encoding="utf-8")
        sleep = pasta / "sleep"
        sleep.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        sleep.chmod(0o755)
        env = dict(os.environ, PATH=f"{pasta}{os.pathsep}{os.environ.get('PATH', '')}")
        r = subprocess.run(["bash", "--norc", "--noprofile", "-c", laco()], env=env, capture_output=True, text=True,
                           timeout=60)
        vistas = pasta / "vistas"
        return r, len(vistas.read_text(encoding="utf-8").splitlines()) if vistas.exists() else 0

    def test_pr_mesclado_com_checks_pendentes_sai_na_segunda_volta(self):  # o caso P-N5
        r, vistas = self.rodar(["OPEN", "MERGED"], checks=8)
        self.assertEqual((r.stdout, r.returncode, vistas), ("fim=MERGED\n", 0, 2))

    def test_pr_fechado_sai(self):
        r, vistas = self.rodar(["CLOSED"])
        self.assertEqual((r.stdout, r.returncode, vistas), ("fim=CLOSED\n", 0, 1))

    def test_checks_sem_pendencia_saem_com_o_codigo(self):
        for codigo in (0, 1):
            with self.subTest(codigo=codigo):
                r, vistas = self.rodar(["OPEN"], checks=codigo)
                self.assertEqual((r.stdout, r.returncode, vistas), (f"fim=checks:{codigo}\n", 0, 1))

    def test_pendente_o_tempo_todo_sai_no_teto_depois_de_17_leituras(self):
        r, vistas = self.rodar(["OPEN"], checks=8)
        self.assertEqual(r.stdout, "fim=teto\n")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(vistas, 17)

    def test_gh_que_falha_sai_com_erro(self):
        r, vistas = self.rodar(["OPEN"], falha=True)
        self.assertEqual((r.stdout, r.returncode, vistas), ("fim=erro\n", 0, 0))


class LacoDoLog(unittest.TestCase):
    """BG-MORRE-TURNO: a linha de lançamento da skill, com `git` falso, grava `rc=` no log; o laço sai nele ou no teto."""

    def rodar(self, codigo_do_git=None):
        pasta = pasta_com_gh()
        (pasta / "git").write_text(f"#!/bin/sh\necho 'git falso'\nexit {codigo_do_git}\n", encoding="utf-8")
        (pasta / "sleep").write_text('#!/bin/sh\necho s >> "$(dirname "$0")/sonos"\n', encoding="utf-8")
        for nome in ("git", "sleep"):
            (pasta / nome).chmod(0o755)
        env = dict(os.environ, PATH=f"{pasta}{os.pathsep}{os.environ.get('PATH', '')}")
        log = pasta / "envio.log"
        if codigo_do_git is not None:
            envio = com_log(lancamento().replace("<envio>", "git push origin melhoria/x"), log)
            subprocess.run(["bash", "--norc", "--noprofile", "-c", envio], env=env, timeout=60)
        r = subprocess.run(["bash", "--norc", "--noprofile", "-c", com_log(laco_do_log(), log)], env=env,
                           capture_output=True, text=True, timeout=60)
        sonos = pasta / "sonos"
        return r, len(sonos.read_text(encoding="utf-8").splitlines()) if sonos.exists() else 0

    def test_envio_que_passa_sai_na_hora(self):
        r, sonos = self.rodar(0)
        self.assertEqual((r.stdout, r.returncode, sonos), ("fim=rc=0\n", 0, 0))

    def test_envio_que_falha_sai_e_mostra_rc_1(self):
        r, sonos = self.rodar(1)
        self.assertEqual((r.stdout, r.returncode, sonos), ("fim=rc=1\n", 0, 0))

    def test_log_sem_rc_sai_no_teto_depois_de_17_voltas(self):
        r, sonos = self.rodar()
        self.assertEqual((r.stdout, r.returncode, sonos), ("fim=teto\n", 1, 17))

    def test_laco_do_log_dentro_do_teto(self):
        voltas = int(re.search(r"seq 1 (\d+)", laco_do_log()).group(1))
        intervalo = int(re.search(r"sleep (\d+)", laco_do_log()).group(1))
        self.assertLessEqual(voltas * intervalo, 540)


class TextoDaSkill(unittest.TestCase):
    def test_frontmatter_e_tech_lead_carrega(self):
        texto = SKILL.read_text(encoding="utf-8")
        self.assertRegex(texto, r"\A---\nname: esperar-estado\ndescription: \S")
        self.assertRegex(TECH_LEAD.read_text(encoding="utf-8"), r"(?m)^skills: .*\besperar-estado\b")

    def test_blocos_sem_espera_proibida_e_dentro_do_teto(self):
        self.assertGreaterEqual(len(BLOCOS), 1)
        for bloco in BLOCOS:
            with self.subTest(bloco=bloco[:40]):
                for proibido in ("sh -c", "timeout", "--watch", "run_in_background"):
                    self.assertNotIn(proibido, bloco)
        voltas = int(re.search(r"seq 1 (\d+)", laco()).group(1))
        intervalo = int(re.search(r"sleep (\d+)", laco()).group(1))
        self.assertLessEqual(voltas * intervalo, 540)

    def test_skill_sem_palavra_de_marcador_dos_hooks(self):
        marcador = re.compile(r"\b(merge|push|pull|create|ready|review|edit|close|label|api)\b", re.I)
        self.assertEqual(marcador.findall(SKILL.read_text(encoding="utf-8")), [])


class BlocosPassamPelosHooks(unittest.TestCase):
    executar_em_lote = test_hooks.Hooks.executar_em_lote
    executar_fixture = test_hooks.Hooks.executar_fixture
    _pasta_temporaria = test_hooks.Hooks._pasta_temporaria
    depende_de_pid_ou_trava = staticmethod(test_hooks.Hooks.depende_de_pid_ou_trava)

    AMBIENTES = {
        "forge": {"arquivos": {".claude-plugin/plugin.json": "{\"name\": \"forge\"}\n"}, "forge": False,
                  "git": [{"branch": "melhoria/x"}]},
        "projeto": {"git": [{"branch": "feature/x"}]},
    }

    LOG = "/home/u/.forge-tmp/envio.log"

    def test_blocos_saem_0_no_parecer_e_na_conformidade(self):
        """Os blocos e a linha de lançamento com o envio de verdade (`git` na branch do ambiente), com `<log>` literal."""
        casos = []
        for hook in ("parecer", "conformidade"):
            for nome, ambiente in self.AMBIENTES.items():
                envio = lancamento().replace("<envio>", f"git push origin {ambiente['git'][0]['branch']}")
                for i, bloco in enumerate([*BLOCOS, envio]):
                    bloco = com_log(bloco, self.LOG)
                    entrada = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_use_id": "toolu_9",
                               "agent_type": "forge:tech-lead", "tool_input": {"command": bloco.strip()}}
                    dados = dict(ambiente, env={"HOME": "{tmp}/home"}, entrada=entrada, esperado={"codigo": 0})
                    casos.append((f"{hook}/{nome}-{i}", Fixture(Path(hook) / f"esperar-{nome}-{i}.json", dados)))
        self.assertEqual(len(casos), 4 * (len(BLOCOS) + 1))
        self.assertEqual(self.executar_em_lote(casos), len(casos))


if __name__ == "__main__":
    unittest.main()
