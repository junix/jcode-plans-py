build:
    uv build

test:
    uv run -m pytest src/jcode_plans/tests/ -v

install:
    @echo "Library package — no binary to install"
