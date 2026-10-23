# Nix Toolbox за Codex

Оперативен skill, който избира Nix инструменти според задачата, изпълнява
проверки и използва резултатите като доказателства. Помага при липсващи команди
и библиотеки, различни development/CI среди, Nix build грешки, пакетиране и
анализ на зависимости. Вход: [SKILL.md](skills/nix-toolbox/SKILL.md).

Работи самостоятелно. Независими проверки могат да се делегират, когато Codex
има агентни инструменти и задачата разрешава използването им. Инструкциите са
на английски; отговорите следват езика на потребителя. Няма зависимост от
конкретен GPT, Qwen, GLM или DeepSeek API.

## Инсталиране на друга Linux машина

Нужни са Git, работещ Nix с `nix-command`/`flakes` и локален Codex.
Няма изискване дистрибуцията да е NixOS. Поддържаните toolbox outputs са
`x86_64-linux` и `aarch64-linux`.

```bash
git clone https://github.com/cheirekov/nixCodexSKILL.git
cd nixCodexSKILL
nix shell --no-write-lock-file ./skills/nix-toolbox#python3 -c python3 scripts/install_local.py
```

Инсталаторът:

- Свързва `~/.agents/skills/nix-toolbox` към skill-а в клонираното Git репо.
- Реализира заключения MCP-NixOS в `~/.local/share/nix-toolbox/mcp-nixos`.
  Постоянната Nix връзка запазва runtime closure-а при garbage collection.
- Добавя `[mcp_servers.mcp-nixos]` в `$CODEX_HOME/config.toml` или стандартния
  `~/.codex/config.toml`, без промяна на останалите настройки. При промяна пази
  резервно копие с ограничени права в Codex `backups/`.
- Отказва да замени чужда skill директория, различен MCP запис или управляван
  чрез symlink `config.toml`. Повторното изпълнение обновява runtime-а според
  lock-а и запазва съществуващия съвпадащ MCP запис.

Самият Python скрипт изисква Python 3.11+. Командата по-горе го осигурява чрез
същия lock; няма нужда да обновявате системния Python. Ако вече имате такава
версия, може директно `python3 scripts/install_local.py`.
Инсталацията може да изтегля store paths и изключва remote builders за своя
build. При собствен post-build hook проверете неговите ефекти предварително.

След инсталация skill-ът трябва да е наличен на следващия ход. За първа проверка
отворете нов локален разговор в желания проект. Проверете MCP връзката с
`/mcp`; ако новият сървър не се появи, използвайте Settings → MCP servers →
Restart. Не е нужно да прекъсвате друга активна задача.

[Официални skill locations и symlinks](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills),
[официална MCP конфигурация](https://learn.chatgpt.com/docs/extend/mcp).

## Първа реална задача

Например:

```text
Използвай $nix-toolbox за този проект. Първо провери дали MCP-NixOS е достъпен.
Без промени по файловете определи как да изпълним съществуващите тестове в
възпроизводима среда. Запази проектния pin и използвай само нужните инструменти.
Покажи командите, резултатите и какво остава непроверено.
```

За по-полезен тест заменете общата задача с действителния проблем: липсваща
библиотека, неуспешен build, различие между local и CI, или голям closure.
Изричното `$nix-toolbox` проверява изпълнението на workflow-а. За отделна проба
на автоматичното разпознаване задайте същата задача без името на skill-а.

## Инструменти

Toolbox flake-ът има отделни apps: `statix`, `deadnix`, `nixfmt`, `nix-locate`,
`nom`, `nix-diff`, `nix-init`, `nix-update`, `nix-fast-build`, `mcp-nixos`.
Изтегля се само избраният инструмент и зависимостите му.

```bash
nix run --no-write-lock-file ./skills/nix-toolbox#statix -- check /absolute/project
nix run --no-write-lock-file ./skills/nix-toolbox#deadnix -- --fail /absolute/project
nix shell --no-write-lock-file ./skills/nix-toolbox#jq -c jq --version
```

Toolbox pin-ът избира версиите на помощните инструменти. Проектният pin остава
източникът за зависимостите и опциите на приложението. `nix-locate` се нуждае
от съответна file database; инструментът не я генерира автоматично.

[MCP-NixOS](https://github.com/utensils/mcp-nixos) добавя търсене на пакети,
опции и документация. Инсталираният от този lock пакет е `3.0.1`; не се следва
автоматично последната PyPI версия. Skill-ът работи и без MCP.
Upstream код и документални корпуси не са vendored в това репо.

[Процедури](skills/nix-toolbox/references/tools.md) ·
[Граници на изпълнение](skills/nix-toolbox/references/execution.md) ·
[Проверки и ограничения](VALIDATION.md)

## Обновяване

```bash
git pull --ff-only
nix shell --no-write-lock-file ./skills/nix-toolbox#python3 -c python3 scripts/install_local.py
```

За промяна на версиите, поддържащият репото обновява и проверява lock-а:

```bash
cd skills/nix-toolbox
nix flake update nixpkgs
nix flake check --all-systems --no-build --no-write-lock-file
```

Прегледайте version/flag промените и native изпълнението преди commit.
Project inputs не се обновяват като страничен ефект.

Проверки на нашия код от корена на репото:

```bash
nix shell --no-write-lock-file ./skills/nix-toolbox#python3 -c python3 -B -m unittest discover -s tests -v
nix flake check --all-systems --no-build --no-write-lock-file ./skills/nix-toolbox
```

## Източници и лиценз

[best-of-nix](https://github.com/tolkonepiu/best-of-nix) служи за откриване на
инструменти. Допълващи knowledge skills: [nix-skills](https://github.com/olafkfreund/nix-skills),
[nixos-ai-skill](https://github.com/marceloeatworld/nixos-ai-skill),
[juspay/skills](https://github.com/juspay/skills). Не е необходимо да зареждате
всички заедно. Проверявайте техните версии, лицензи и приложимост към проекта.

[MIT](LICENSE) за оригиналния код и инструкции тук. Външните инструменти запазват
собствените си лицензи; Nixpkgs ги доставя като отделни зависимости.
