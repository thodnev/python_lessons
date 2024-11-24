## Git Workflow

Рассмотрим создание веток, коммиты и слияние веток.

Я создам новый репозиторий (в будущем это будет *субмодуль*).

Создаем репозиторий.

`git init workflow` `&&` `cd workflow`

`git init -b main workflow` (`--initial-branch=main`) `&&` `cd workflow`

Посмотрим, где мы:

`git status`

Сделаем пару тестовых коммитов в основную ветку.

(Я отключу *для данного* репозитория автоподпись):

`git config --list`

`git config --local commit.gpgsign false`

`nvim CHANGELOG.md`


```text
## Imitate some changes made to our software

- Initial stuff to commit
```

Сделаем коммит:

    git add CHANGELOG.md
    git commit -a -m "docs: initial"

Посмотрим его:

`git log --oneline --graph --all`


Сделаем еще коммит.

`git commit -a -m "docs: initial"`
(свитч `-a` показывает что надо автоматом положить все файлы, которые Git *трекает* и добавить в новый коммит).


Теперь симитируем, что мы имеем репозиторий в каком-то состоянии. Репозиторий публичный.
И мы хотим поработать над какой-то фичей.

Допустим, имитируем добавление функционала.

Прежде всего, надо ответвиться. Создам ветку *dev*, в которой и разработаю свою фичу.

Создаем ветку.
`git checkout -b dev`

В ней сделаем два коммита. Один имит. добавление фичи, а второй – добавление тестов для этой фичи.

Добавим такую строчку в файл:

    - Adding new feature in separate branch


Посмотрим, что мы изменили. Для этого есть команда `git diff`:
- Просто `git diff` покажет изменения рабочей директории относительно последнего коммита (HEAD)
- Текущая директория относительно коммита: `git diff 47b5524`
- Один коммит относительно другого (важен порядок):
`git diff 47b5524..346ed3f`
- И т.д. Например, только конкретные файлы между двумя коммитами:
`git diff 47b5524..346ed3f -- CHANGELOG.md`

Перед коммитом желательно делать `git diff` чтобы посмотреть изменения. Часто бывает, что разработчик меняя что-то одно, вносит изменения в другое. Например, добавляет пробел в ту функцию, которой он не касался.

Посмотрели. Теперь можем коммитить в нашу ветку.

`git commit -am 'feat: new feature'`

Посмотрим нашу историю:
`git log --oneline --graph --all`

Для разнообразия, сделаем еще один коммит. Мы имитируем разработку каких-то фич в отдельной ветке. Сейчас коммитим тесты.

Закоммитили. У нас в итоге такой файл:

    ## Imitate some changes made to our software

    - Initial stuff to commit
    - Our 2nd line to commit

    - Adding new feature in separate branch
    - Adding tests alongside with this feature


А теперь мы хотим инкорпорировать эти фичи в основную ветку проекта. Тут уже речь идет о слиянии (merge) коммитов.

### Merging branches

Вернемся в ветку `main`. Когда делаем merge, хорошо бы возвращаться в ветку, куда будем сливать.

`git checkout main`


Попробуем слить коммиты. Есть несколько вариантов (стратегий слияния):
- **Fast-Forward**. Суть ее в том, что у нас есть отдельная ветка с коммитами. И их можно добавить в основную ветку просто так (как будто они и были там):
![ff](https://i.sstatic.net/rTxx9.png)
И не будет создаваться отдельного коммита слияния. Так можно экономить на лишних коммитах и держать историю более чистой.
Иногда наоборот надо показать, что это была отдельная фича.
    Для Fast-Forward просто:
    `git merge --ff dev` (часто это по-умолчанию).
    Если он может это сделать, он выполнит.

    В итоге, получим такую историю:

        git log --oneline --graph --all
        * 774d73c (HEAD -> main, dev) test: cool feature tests
        * d697cd1 feat: new feature
        * 346ed3f docs: 2nd line
        * 47b5524 docs: initial

(Мы экспериментируем. Я вернусь назад, как будто не делал слияния. И попробуем другие варианты.) Это можно сделать с помощью
`git reflog`. Он покажет внутрянку при перемещении между командами:

```
$ git reflog
774d73c (HEAD -> main, dev) HEAD@{0}: merge dev: Fast-forward
346ed3f HEAD@{1}: checkout: moving from dev to main
774d73c (HEAD -> main, dev) HEAD@{2}: commit: test: cool feature tests
d697cd1 HEAD@{3}: commit: feat: new feature
346ed3f HEAD@{4}: checkout: moving from main to dev
346ed3f HEAD@{5}: commit: docs: 2nd line
47b5524 HEAD@{6}: commit (initial): docs: initial

$ git reset --hard HEAD@{1}
HEAD is now at 346ed3f docs: 2nd line

$ git log --oneline --graph --all
* 774d73c (dev) test: cool feature tests
* d697cd1 feat: new feature
* 346ed3f (HEAD -> main) docs: 2nd line
* 47b5524 docs: initial
```

Попробуем другие варианты слияния.

- Классический merge (не Fast-Forward). Он же, `ort`. Делаем:

`git merge --no-ff dev -m "merge: incorporate cool feature and tests"`

После увидим *Merge made by the 'ort' strategy*.

Если не указать сообщение самому, то откроется редактор. То же самое (примерно), как и с коммитами.

И теперь посмотрим историю коммитов и ветвление:

`git log --oneline --graph --all`

Увидим такую штуку:

    git log --oneline --graph --all
    *   7d83a67 (HEAD -> main) merge: incorporate cool feature and tests
    |\  
    | * 774d73c (dev) test: cool feature tests
    | * d697cd1 feat: new feature
    |/  
    * 346ed3f docs: 2nd line
    * 47b5524 docs: initial

То есть, был создан отдельный коммит слияния (merge commit).

То что мы увидим, это хороший *Git Workflow*. Но не совсем. 

Поскольку, перед слиянием в main, мы не проверили возможность слияния. И не зацепили изменения из main в нашу ветку.

Обычно перед merge в *main*, пытаются сперва сделать merge из *main* в нашу ветку. Т.е.

    main -> dev
    dev -> main
Пока мы были заняты *dev*, в *main* могли произойти изменения. Хорошо бы их учесть.

Тут мы приходим к разговору о конфликтах при слиянии.

#### Конфликты при слиянии

До этого мы работали одни. Теперь будем имитировать ситуацию, когда пока мы работали над фичей в отдельной ветке, проект жил своей жизнью. И в main появились свои коммиты.

Перейдем в main и добавим коммиты.

`git checkout main`

- Добавим коммит, который не затрагивает контекста, над которым мы работали в другой ветке и попробуем слить его.

```
git diff 346ed3f
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 892434d..b432b93 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -1,4 +1,4 @@
 ## Imitate some changes made to our software
-
+Add some description, imitating changes in main.
 - Initial stuff to commit
 - Our 2nd line to commit
```

```
git diff HEAD..dev
diff --git a/CHANGELOG.md b/CHANGELOG.md
index b432b93..be9d87b 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -1,4 +1,7 @@
 ## Imitate some changes made to our software
-Add some description, imitating changes in main.
+
 - Initial stuff to commit
 - Our 2nd line to commit
+
+- Adding new feature in separate branch
+- Adding tests alongside with this feature
```
Видим, что изменения не пересекаются.

Теперь сливаем нашу ветку.

`git merge --ff dev`

Видим что FF он не сделал. Но мы слили без проблем:
```
git log --oneline --graph --all
*   d866ad1 (HEAD -> main) merge branch 'dev'
|\  
| * 774d73c (dev) test: cool feature tests
| * d697cd1 feat: new feature
* | f70975b docs: add description
|/  
* 346ed3f docs: 2nd line
* 47b5524 docs: initial
```

Сделаем это правильно. Вернемся на ветку dev и попробуем слить изменения из main перед слиянием dev -> main.

`git checkout dev`

`git merge main -m "merge: incorporate main changes`

`git checkout main`

`git merge --ff dev`

Теперь он смог сделать FF. И мы правильно поступили, что разрулили изменения в отдельной ветке.


До этого контексты не пересекались.
Теперь имитируем ситуацию, когда мы меняли одно и то же в двух ветках. (Возвращаемся до слияния)

Создаем еще один коммит в main.

Поменяем в нем строку:
`Initial stuff to commit. SOME MORE STUFF IN MAIN`

`git commit -am "fix: change in main"`

И вернемся в dev. И в нем поменяем ту же строку.
`git checkout dev`

`nvim CHANGELOG.md`

`Initial stuff to commit. ....NOW DEV CHANGES...`

`git commit -am "fix: change in dev"`


Вот такое состояние репозитория:
```
git log --oneline --graph --all
* 7ee2d51 (HEAD -> dev) fix: change in dev
* 774d73c test: cool feature tests
* d697cd1 feat: new feature
| * 5df5ef1 (main) fix: change in main
| * f70975b docs: add description
|/  
* 346ed3f docs: 2nd line
* 47b5524 docs: initial
```

Т.е. в коммитах:
- *(main) fix: change in main*
- и *(dev) fix: change in dev*

Мы меняли одну и ту же строку.

Если мы теперь попробуем их слить, то возникнет конфликт.

Пробуем сливать правильно. Т.е. сначала сливаем *main* в *dev*.

`git merge main`

Видим сообщение:
```
Auto-merging CHANGELOG.md
CONFLICT (content): Merge conflict in CHANGELOG.md
Automatic merge failed; fix conflicts and then commit the result.
```

Т.е. имеем конфликт в CHANGELOG.md.

Если теперь посмотрим этот файл
(`cat CHANGELOG.md`) то увидим, что он изменился.

В нем теперь такой фрагмент:
    
    <<<<<<< HEAD

    - Initial stuff to commit. ....NOW DEV CHANGES...
    =======
    Add some description, imitating changes in main.
    - Initial stuff to commit. SOME MORE STUFF IN MAIN
    >>>>>>> main
    

Значит Git не разобрался. Есть две версии:
- Версия из текущей ветки (dev)
  ```
  <<<<<<< HEAD
  
  - Initial stuff to commit. ....NOW DEV CHANGES...
  ```
- Разделитель `=======`
- Версия из ветки, которую сливаем (main):
  ```
  Add some description, imitating changes in main.
  - Initial stuff to commit. SOME MORE STUFF IN MAIN
  >>>>>>> main
  ```


Git просит нас разрулить конфликт. Выбрать одну из версий, которая нас устраивает. Или вообще переписать эти строки по-другому.