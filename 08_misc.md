## Systemd services

Сперва посмотрим, какие есть сервысы в системе:

`systemctl list-unit-files --type service`

Возьмем из него какое-то описание службы за шаблон. Например, у меня это `cronie.service`

Смотрим его статус:

`systemctl status cronie.service`

После просмотра статуса я вижу путь описания:
`/usr/lib/systemd/system/cronie.service`

Посмотрим его:
`cat /usr/lib/systemd/system/cronie.service`

Я вижу такое описание:
```
[Unit]
Description=Command Scheduler
After=auditd.service nss-user-lookup.target systemd-user-sessions.service time-sync.target ypbind.service autofs.service

[Service]
EnvironmentFile=-/etc/sysconfig/crond
ExecStart=/usr/sbin/crond -n $CRONDARGS
ExecReload=/bin/kill -URG $MAINPID
KillMode=process
Restart=on-failure
RestartSec=30s

[Install]
WantedBy=multi-user.target
```

Более подробно о пунктах описания можно почитать в [`man systemd.unit`](https://man.archlinux.org/man/systemd.unit.5)


Есть общие сервисы (системные), а есть для пользователя (systemd user service). Будем использовать вторые. Более подробно об этом можно почитать тут:
- https://wiki.archlinux.org/title/Systemd/User#How_it_works
- https://wiki.archlinux.org/title/Systemd#Writing_unit_files


В одном из документов мы видим пути, по которым можно положить описание user-сервиса.
Одни из путей:
- `~/.local/share/systemd/user/`
- `~/.config/systemd/user/` - для тех, что создает сам пользователь. Сюда и сложим

Сходим сюда и посмотрим, что тут есть:
`cd ~/.config/systemd/user`

(у меня тут пусто)

Скопируем сюда нашу службу (шаблон и подправим его)

`cp /usr/lib/systemd/system/cronie.service ~/.config/systemd/user/myservice.service`


```
[Unit]
Description=My Server

[Service]
Type=exec
WorkingDirectory=/...trident.../
ExecStart=java -Xmx1024M -Xms1024M -jar server.jar
#User=trident
Restart=on-success

[Install]
WantedBy=default.target
```

Хорошо бы [создать отдельного пользователя](https://superuser.com/questions/77617/how-can-i-create-a-non-login-user/515909#515909) `trident`, под которым и запускать этот сервис:

`sudo useradd --system --no-create-home --user-group trident`


Перед тем, как описывать в модуле реальный сервер, симитируем его работу. Сервером будет что-то, что:
- Выводит сообщение в терминал
- Добавляет запись в лог
- Остается запущенным в течение продолжительного времени

Можем написать такой bash-скрипт для имитации:
```bash
#!/usr/bin/bash

workdir="$(pwd)"
curdate="$(date)"
ret=$(echo -e "${workdir}\t${curdate}")
file=~/imitate-server.log

# write to file
echo "${ret}" >> "${file}"
# output to screen
echo -e "Starting server @ ${workdir}...\n${curdate}"

# Stay open
sleep 1h
```

Сохраним как `imitate-server.sh` и сделаем ему права на запуск:

`chmod +x ./imitate-server.sh`


Затем проверим, запустив: `./imitate-server.sh`.
Должен произойти вывод на экран:
```[thd@mi educ]$ ./imitate-server.sh 
Starting server @ /home/thd/Work/python/educ...
Sun Nov 24 10:32:32 PM CET 2024
```
а также добавиться запись в лог `~/imitate-server.log`:
```
/home/thd/Work/python/educ	Sun Nov 24 10:32:32 PM CET 2024
```

Теперь можем проверить как он работает, сделав для него systemd-юнит:
```
[Unit]
Description=Trident Server

[Service]
Type=exec
WorkingDirectory=/home/thd/Work/python/educ
ExecStart=imitate-server.sh

[Install]
WantedBy=default.target
```

Для того чтобы можно было автоматически запускать сервис независимо от входа пользователя в систему, необходимо чтобы:

- Был включен [lingering](https://wiki.archlinux.org/title/Systemd/User#Automatic_start-up_of_systemd_user_instances). Lingering - это возможность systemd быть активным даже если не выполнен вход в пользователя:

    `loginctl enable-linger myusername`

    Проверить можно командой:

    `loginctl list-users`

    (в колонке LINGER должно быть "yes")
- У юнита должна быть зависимость от `default.target` вместо `multi-user.target`:
    
    ```
    [Install]
    WantedBy=default.target
    ```



Ключевые команды:

- Перезагрузить список сервисов (после редактирования файла описания):

    `systemctl --user daemon-reload`

- Посмотреть статус сервиса

    `systemctl --user status trident`

- Запустить сервис:

    `systemctl --user start trident`

- Остановить сервис:

    `systemctl --user stop trident`

- Перезапустить сервис:

    `systemctl --user restart trident`

- Включить автозапуск сервиса:

    `systemctl --user enable trident`

- Выключить автозапуск сервиса:

    `systemctl --user disable trident`

- Посмотреть логи сервиса:

    `systemctl --user status trindent`

    и

    `journalctl --user -u trident`



Будем пробовать запускать сервис через `screen`, чтобы к нему можно было потом присоединиться.

Это можно сделать заменив просто имя скрипта на:

`screen -m -D -S trident imitate-server.sh`

Тут:
- `-m -D` запускает screen в datached-режиме, но не создает новый процесс с помощью fork. Таким образом коренной процесс screen не закроется до запущенного в нем. `-m` заставляет игнорировать отсутствие реального терминала (у нас вместо него systemd)
- `-S trident` создает именованную сессию. Чтобы потом можно было подключаться к ней с помощью `screen -r trident`
- `imitate-server.sh` то, что необходимо выполнить



Добавим дополнительных опций:
- `After=network.target` в секцию `[Unit]`. Тут можно перечислить зависимости, т.е. что должно запуститься сперва перед запуском сервера (пока тут сеть)
- `Restart=on-success`. При завершении со статусом 0, перезапускать. Посмотреть статус завершенного процесса можно как `echo $?` непосредственно после завершения
- `RestartSec=2s` - Перезапускать через 2 секунды после падения (чтобы не было кучи перезапусков если что-то пошло не так)
- `TimeoutStopSec=40s` - Время, сколько дать серверу на нормальное завершение (сколько обычно он завершается после подачи Ctrl+C)
- И т.д.

Более подробно об опциях и формате описания сервиса можно почитать в:
- [`man systemd.service`](https://man.archlinux.org/man/systemd.service.5.en)
- [`man systemd.unit`](https://man.archlinux.org/man/systemd.unit.5)

Получим:
```
[Unit]
Description=Trident Server
After=network.target

[Service]
Type=exec
WorkingDirectory=/home/thd/Work/python/educ
ExecStart=screen -m -D -S trident imitate-server.sh
Restart=on-success
RestartSec=2s
TimeoutStopSec=40s

[Install]
WantedBy=default.target
```