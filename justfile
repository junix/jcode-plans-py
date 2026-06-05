
set shell := ["bash", "-euo", "pipefail", "-c"]

# 解释型脚本安装目录（与架构无关，ADR-749）
install_bin := home_directory() / "sync" / "bin"
# 构建（Release 模式）
build:
    uv build

# 运行测试
test:
    uv run -m pytest src/jcode_plans/tests/ -v

# 安装到 ~/sync/bin/
install: build
    @echo "Library package — no binary to install"

update-junix-git:
    #!/usr/bin/env bash
    set -euo pipefail
    pkgs="$(python3 -c "import tomllib; from pathlib import Path; data = tomllib.loads(Path('pyproject.toml').read_text()); sources = data.get('tool', {}).get('uv', {}).get('sources', {}); pkgs = sorted(name for name, spec in sources.items() if isinstance(spec, dict) and spec.get('git', '').startswith('https://github.com/junix/')); print(' '.join(pkgs))")"
    if [[ -z "$pkgs" ]]; then
        echo "No github.com/junix git dependencies found in pyproject.toml"
    else
        for pkg in $pkgs; do
            uv lock --upgrade-package "$pkg"
        done
    fi

build-locked: build

install-locked: install
