from __future__ import annotations

import os
import tomllib
from tomllib import TOMLDecodeError
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .hooks.lifecycle import HookConfig
from .settings import RuntimeSettings


@dataclass(slots=True)
class LoadedConfig:
    raw: Dict[str, Any]
    settings: RuntimeSettings
    hooks: List[HookConfig] = field(default_factory=list)
    permission_rules: Dict[str, str] = field(default_factory=dict)


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        return os.path.expandvars(value)
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    return value


def load_config(path: str | Path = "config.toml") -> LoadedConfig:
    config_path = Path(path)
    if config_path.exists():
        try:
            raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
        except TOMLDecodeError as exc:
            raise ValueError(f"Invalid TOML in {config_path}: {exc}") from exc
    else:
        raw = {}

    raw = _expand_env(raw)
    model_cfg = raw.get("model", {})
    lsp_cfg = raw.get("lsp", {})
    hooks_cfg = raw.get("hooks", [])

    settings = RuntimeSettings(
        model=model_cfg.get("name", "moonshot-v1-128k"),
        provider=model_cfg.get("provider", "kimi"),
        base_url=model_cfg.get("base_url", "https://api.moonshot.cn/v1"),
        lsp_enabled=bool(lsp_cfg.get("enabled", True)),
    )

    hooks = [
        HookConfig(
            event=item.get("event", "tool_call_after"),
            command=item.get("command", ""),
            matcher=item.get("matcher"),
            timeout_sec=int(item.get("timeout_sec", 30)),
        )
        for item in hooks_cfg
        if item.get("command")
    ]

    return LoadedConfig(
        raw=raw,
        settings=settings,
        hooks=hooks,
        permission_rules=raw.get("permissions", {}),
    )
