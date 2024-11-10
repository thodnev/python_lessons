### Intro

- Дистрибутив. Могу порекомендовать любой Arch-based, например,
  [Manjaro](https://manjaro.org/).

  Из вариантов Manjaro, советую *Manjaro KDE Plasma*

- [Markdown - Basic Syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)

- Git. Для Windows есть официальная сборка [Git for Windows](https://gitforwindows.org/)
  У него в комплекте есть терминал.

  **Важно:** при установке он будет спрашивать разные опции. Например, выполнять ли автопреобразование LF<->CRLF - его выполнять не надо. И другие опции должны быть максимально
  в духе Linux-окружения

- Terminal. Например, [Kitty](https://sw.kovidgoyal.net/kitty/),
  [Alacritty](https://alacritty.org/),[WezTerm](https://wezfurlong.org/wezterm/index.html),
  [Extraterm](https://extraterm.org/) или [MinTTY](https://mintty.github.io/).
  Kitty нужно настраивать.
  MinTTY поставляется в комплекте с Git for Windows

- В дополнение к терминалу, нам понадобится минимальное Linux-окружение. Это bash, cat, и т.д.
  
  Обычно, оно входит в состав Git for Windows, и его достаточно.  Для этого:
  - В `PATH` добавить: `C:\Program Files\Git`
  - В директорию `C:\Program Files\Git` покласть какой-то `bashenv.bat`:
    ```
    @echo off
    git-cmd.exe --command=usr/bin/bash.exe
    ```
    Можно также добавить флаги: `git-cmd.exe --command=usr/bin/bash.exe -l -i`
  
  Или можно поставить полноценный MinGW со всеми утилитами.

  WSL или Cygwin лучше не использовать. Они не совсем нативные.


- Python. При установке надо:
  - ставить pip
  - добавлять в PATH
  - компилировать стандартную библиотеку
  - можно поставить и tk-библиотеку

- Python-окружение.
  
  - `pip` должен работать нормально.
  - Команды ниже выполняем из обычной командной строки
  - Ставим `pipx`:
    ```bash
    pip install --user pipx
    ```
    Pipx -- это инструмент, позоволяющий ставить каждый пакет Python в отдельное изолированное окружение. Т.е. одни и те же библиотеки разных версий в разных пакетах не мешают друг другу.
  - В pipx попробуем поставить `ipython`:
    ```bash
    pipx install ipython
    ```

    IPython расширяет возможности оболочки. В часности, у него есть редактирование многострочных
    строк, подсветка синтаксиса и т.д.
    И есть расширения вроде `%timeit` и `%time`

