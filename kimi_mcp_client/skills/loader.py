from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Skill:
    name: str
    description: str
    body: str
    path: str


def _parse_skill(path: Path) -> Skill:
    text = path.read_text(encoding="utf-8")
    name = path.parent.name
    description = ""
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            front = text[3:end].strip().splitlines()
            body = text[end + 4 :].strip()
            for line in front:
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip()
                if line.startswith("description:"):
                    description = line.split(":", 1)[1].strip()
    if not description:
        description = body.splitlines()[0] if body else ""
    return Skill(name=name, description=description, body=body, path=str(path))


def _collect_paths(extra_paths: list[str] | None = None) -> list[Path]:
    roots = [
        Path.home() / ".kimi" / "skills",
        Path.home() / ".claude" / "skills",
        Path.home() / ".agents" / "skills",
    ]
    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        roots.append(parent / ".kimi" / "skills")
    for p in extra_paths or []:
        roots.append(Path(p).expanduser())
    return roots


def load_skills(extra_paths: list[str] | None = None) -> list[Skill]:
    logger = logging.getLogger("kimi.skills")
    skills: list[Skill] = []
    for root in _collect_paths(extra_paths):
        if not root.exists():
            continue
        for file_path in root.glob("**/SKILL.md"):
            try:
                skills.append(_parse_skill(file_path))
            except Exception as exc:
                logger.warning("Failed to parse skill file %s: %s", file_path, exc)
                continue
    return skills
