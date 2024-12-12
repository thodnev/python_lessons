### Получение копии удаленного репозитория с ветками

Если что-то пошло не так с локальным репозиторием, один из вариантов это восстановить его из удаленного репозитория (или сделать копию в другой директории):

1.  `git clone git@github.com:lostyawolfer/lostyas_tag.git testrepo`
    Создаст копию удаленного репозитория в директории `testrepo`

    И `cd testrepo`

2.  По-умолчанию, клонируется дефолтная ветка.
    Однако, у проекта может быть несколько веток. Чтобы посмотреть их все
    (включая удаленные), можно воспользоваться
    `git branch -v --all`.

    Видим такую картину:
    ```
    git branch -v --all
    * master                b69e18b deleting everything
    remotes/origin/HEAD   -> origin/master
    remotes/origin/legacy c3574b1 last commit
    remotes/origin/master b69e18b deleting everything
    ```

    Тут мы видим, что вытянули ветку `master`. А на удаленном
    сервере еще есть `legacy`.

    Чтобы получить все ветки (выкачать), можно воспользоваться
    командой `git fetch`:

    `git fetch origin legacy` - для одной ветки.
    Или для всех веток:
    `git fetch --all`

    Теперь они у меня скачаны.
3.  И чтобы создать в локальном репозитории ветку, которая будет соответстовать
    только что выкачанной, можно использовать обычный `checkout`:

    `git checkout legacy`:

    ```
    $ git checkout legacy
    branch 'legacy' set up to track 'origin/legacy'.
    Switched to a new branch 'legacy'
    ```

    Т.е. локальная ветка теперь трекает удалеенную.

    На этом этапе мы воссоздали локальный репозиторий из
    удаленной копии на сервере.

```
git log --oneline --graph --all
* b69e18b (origin/master, origin/HEAD, master) deleting everything
* 8475ea7 deleting everything
* feafac0 deleting everything
* c688489 deleting everything
* da8113c deleting everything
* f350f4e deleting everything
| * c3574b1 (HEAD -> legacy, origin/legacy) last commit
|/  
* 005f77b fdafsdf
```

[!NOTE] Обычно, ветки берут свое начало где-то. Это значит, что если ветка
`master` взята от ветки `legacy`, то дефолтно выкачивая ветку master,
мы будем тянуть всю историю коммитов.

Если мы этого не хотим, значит надо создать orphan-ветку. Такие ветки не
имеют общего начала в истории (у них свое начало с нуля).
(!) Обычно, orphan-ветка -- это плохо. С ними сложно работать.
Но если нужно именно это (не иметь связи с предыдущими коммитами и другими ветками),
то значит нужно именно orphan.

Как это сделать:
1.  Я удаляю `master`. Удаляю ее принудительно, т.е. с ключом
    `-D` большая.

    `git branch -D master`
2.  Создаю новую ветку, но в orphan-режиме (т.е. без предков):
    `git checkout --orphan master`.

    После этого мы попали на пустую ветку master,
    где еще нету ни одного коммита (и ни одного файла)
3.  Можно физически почистить файлы. Удалить все кроме директории `.git`.
    И добавить первый комиит.
4.  Когда будем пушить эту ветку, надо будет в первый раз сделать
    форс-пуш (`git push -f origin master`)