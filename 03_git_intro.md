### Git Intro

#### Команды Git

- В документации заменяем ` ` на `-`: `man git-init`
- В директории `.git` хранится все, что относится к репозиторию
  Она важна.
- Создание репозитория: `git init`:
  - `git init repo` `&&` `cd repo`
  - `git init .`
- **(!)** Все команды выполняются из директории, в которой находится репозиторий
- Просмотр статуса: `git status`

- Положить файлы под контроль версий:
  - Вручную, с помощью
    ```
    git add myfile otherfile somedir/
    git add one_more_file
    ```
  - Можно убирать из-под working tree с помощью:
    `git rm --cached myfile`

    Но, **(!)** важно не забыть флажок `--cached`

    Для удаления директорий, можно добавить флажок `-r`

- Создание коммитов:
  - `git commit` где мы все укажем вручную:
     
     - Откроется текстовый редактор
       с файлом `.git/COMMIT_EDITMSG`
     - Первая строка в нем самая важная, это oneline-опись коммита.
       А ниже уже могут идти (если это требуется) строки с более детальной описью.
     - Если есть детальная опись коммита, то сразу за первой строкой
       должна быть быть пустая строка, и уже за ней – детальное описание
       (если оно есть; если нету, то тогда только первая строка без всяких отступов)
     - Каждая строка, которая **начинается** с `#` является комментарием при написании
       описи коммита в редакторе. В конечную опись она не входит. Ровно как и После
       закрытия редактор, закомментированные строки никак не сохраняются
     - **НО** вот такая строка `do something   # my comment`
       будет воспринята целиком и комментарий за `#` не засчитается как комментарий.
       Так делать не стоит.

  - Но лучше (**самый расспространенный способ**)
    это сразу указать сообщение

    `git commit -m "feat: initial commit"`

- Команда `git log` позволяет смотреть историю коммитов.
  Ее мы рассмотрим подробно далее


### Шифрование и подписи

- Мы используем шифрование с открытым ключом (следовательно, есть открытый и закрытый ключ).
  Закрытый никому не передается, открытый можно свободно давать всем.
- Для работы с подписями, используем
  открытый пакет GPG. Есть две его вариации (разные версии): `gpg2` и `gpg`. Лучше `gpg2` – он полностью совметим с предыдущей версией и расширяет ее функционал.
  Какой стоит в произвольной системе, мы не знаем: могут стоять оба (тогда используем `gpg2`), а может быть сделан
  симлинк на gpg2 под видом `gpg`.
  Конкретную версию в таком случае можно посмотреть с помощью `gpg --version`:

      gpg (GnuPG) 2.4.5
      ...
- Посмотреть связку ключей:
  
  `gpg2 --list-keys --keyid-format=SHORT`
- Есть 3 категории ключа:
  - `[C]` - Certify  - коренное заверение подписей (CA)
  - **`[A]`** - Authenticate - авторизация (например, на сайте)
  - **`[S]`** - Sign - подпись (например, подписать коммит)
- Сгенерировать ключ:
  
  `gpg2 --expert --full-generate-key`
- Есть разные криптоалгоритмы. Из них есть ненадежные. Или надежные, но при
  каких-то условиях. Например, RSA надежен только при очень длинных ключах
  и он медленный.
  Из новых, есть ECC - на эллиптических кривых (эллиптическая криптография).
  Не все сервисы понимают ECC, но GitHub уже понимает.

  Я выбираю `ECC (set your own capabilities)`

  Дальше...

  Выбираю кривую "Curve 25519"

  Время жизни указываю `5y` – 5 лет

  ...

  Дальше хороший надежный пароль, которым будет открываться этот ключ

- Экспортируем ключ
  - Сперва публичную (открытую часть):
    
    `gpg2 --export --armor B972BB7C  > mykey.public.armor`

  - Публичную часть для SSH:
    
    `gpg2 --export-ssh-key B972BB7C > mykey.public.ssh` 

  - На всякий случай, можно себе сохранить и приватную часть:

    `gpg2 --export-secret-keys`

    Надо не забывать, что приватный ключ должен храниться **всегда
    в зашифрованном виде**.
    Например, с помощью
    
    `--symmetric --cipher-algo AES256`

    Так, цепь команд
    ```
    gpg2 --export-secret-keys B972BB7C | gpg2 --armor --symmetric --cipher-algo AES256 > mysecretkey.asc
    ```
    сперва выведет один приватный ключ на вход другой, которая его зашифрует симметричным алгоритом AES256.
    И в таком виде его уже можно безопасно
    хранить на диске.
    Для импорта можно будет воспользоваться похожей обратной цепочкой:
    ```
    gpg2 mysecretkey.asc | gpg2 --import
    ```
    

    После экспорта, некоторые приватные ключи можно удалить из GPG
    и использовать, например, только с флешки

- Заходим на GitHub в [раздел ключей](https://github.com/settings/keys).
  И можем добавить только SSH-ключ. Этого должно хватить

  **Мы добавляем ТОЛЬКО публичные ключи**

- Настроим Git:
  `git config --list`
  
  В нем надо добавить (`git config --global ...`):
  Для проекта: `git config --local ...`

  `user.signingkey=D077979E9A6CB1EA` - какой ключ

  `commit.gpgsign=true` - автоподпись (чтобы не приходилось каждый раз
  использовать флаг `git commit -S`)

  `gpg.program=gpg2`

  `git config --global user.signingkey B972BB7C`

- Можно настроить `ssh-agent`, чтобы авторизация по SSH (в том числе,
  из-под Git) происходила с помощью gpg и нашего сгенерированного ключа

Лог создания ключа:
```
Possible actions for this ECC key: Sign Certify Authenticate 
Current allowed actions: Sign Certify 

   (S) Toggle the sign capability
   (A) Toggle the authenticate capability
   (Q) Finished

Your selection? A
```

```
Possible actions for this ECC key: Sign Certify Authenticate 
Current allowed actions: Sign Certify Authenticate 

   (S) Toggle the sign capability
   (A) Toggle the authenticate capability
   (Q) Finished

Your selection? Q
```

```
Please select which elliptic curve you want:
   (1) Curve 25519 *default*
   (2) Curve 448
   (3) NIST P-256
   (4) NIST P-384
   (5) NIST P-521
   (6) Brainpool P-256
   (7) Brainpool P-384
   (8) Brainpool P-512
   (9) secp256k1
Your selection? 1
```

```
Please specify how long the key should be valid.
         0 = key does not expire
      <n>  = key expires in n days
      <n>w = key expires in n weeks
      <n>m = key expires in n months
      <n>y = key expires in n years
Key is valid for? (0) 5y
Key expires at Fri 02 Nov 2029 02:46:04 PM CET
Is this correct? (y/N) y
```

```
GnuPG needs to construct a user ID to identify your key.

Real name: thodnev
Email address: thodnev@gmail.com
Comment: Master Git test key
You selected this USER-ID:
    "thodnev (Master Git test key) <thodnev@gmail.com>"
```



## Extra
- cGit – встроенный web-интерфейс git, использующийся во многих opensource- и коммерческих проектах
- [Coventional Commits стандарт](https://www.conventionalcommits.org/en/v1.0.0/#summary) для правильного написания oneline-описаний коммитов
- [Commitizen](https://commitizen-tools.github.io/commitizen/) чтоб энфорсить Coventional Commits стандарт, автоматически
проверяя формат каждого коммит-сообщения

