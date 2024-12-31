## Удаленный доступ к Windows-машине через SSH-туннель

### Сервер OpenSSH
Существует порт официальной OpenSSH для сторонних ОС, который разрабатывается на https://github.com/openssh/openssh-portable

Есть его форк, разрабатываемый как часть PowerShell-инструментария:
https://github.com/PowerShell/openssh-portable

[Релизы](https://github.com/PowerShell/Win32-OpenSSH/releases)
данного форка можно найти на: https://github.com/PowerShell/Win32-OpenSSH

Там же существует [wiki-странчика](https://github.com/PowerShell/Win32-OpenSSH/wiki) с документацией. В ней описаны все отличия порта
от обычного OpenSSH.

### Установка Win32-OpenSSH

Лучше всего скачивать [релиз](https://github.com/PowerShell/Win32-OpenSSH/releases) в виде MSI-пакета. У него [есть аргументы](https://github.com/PowerShell/Win32-OpenSSH/wiki/Install-Win32-OpenSSH-Using-MSI#1-run-msi-installer) командной строки.


1. Скачаем MSI-пакет
2. Установим только серверную часть:
   `msiexec /i <path to .MSI> ADDLOCAL=Server`

   Сам сервер установится в `C:\Program Files\OpenSSH`

   Конфиги будут лежать в `C:\ProgramData\ssh`

3. Запустив в Win+R `services.msc` мы должны увидеть две новых
   службы:
   - `ssh-agent` (*OpenSSH Authentication Agent*)
   - `sshd` (*OpenSSH SSH Server*)

На время конфигурации остановим эти службы:
```
sc stop sshd
sc stop ssh-agent
```

### Порты в Windows

LLama выдает нам диапазоны портов:

> On Windows, the available port range for TCP and UDP is from 0 to 65535. However, ports are categorized into three ranges:
> 
> 1. **Well-Known Ports (0-1023)**: These ports are reserved for specific services and protocols (e.g., HTTP uses port 80, HTTPS uses port 443).
> 
> 2. **Registered Ports (1024-49151)**: These ports can be registered by software applications and are not as strictly controlled as well-known ports.
> 
> 3. **Dynamic or Private Ports (49152-65535)**: These ports are typically used for ephemeral or temporary connections and can be used by applications for dynamic port assignment.
> 
> When configuring applications or services, it's important to choose ports that do not conflict with existing services.

Использовать стандартный 22 порт для SSH не рекомендуется. Его будут сканировать и пытаться сбрутить. Обычно при сканировании, сканеры запускают для первых (начальных диапазонов) портов.
Поэтому, более высокие числа более безопасны.

Будем использовать порт `26969`, потому что это лучше стандартного, в выском диапазоне и хорошо запоминается.


Когда мы меняем порт:
- Нужно чтобы сервер был остановлен
- Новый порт нужно прописать в `sshd_config`
- Нужно поменять правило файрвола на этот порт

Сделаем это.

### Настройка правил файрвола

Найдем предустановленные правила файрвола, относящиеся к ssh:
```
netsh advfirewall firewall show rule name=all | findstr /i "ssh"
```

> `Rule Name:                            OpenSSH SSH Server Preview (sshd)`

Посмотрим это правило в деталях:
```
netsh advfirewall firewall show rule name="OpenSSH SSH Server Preview (sshd)"
```

Поменяем имя правила на `sshd` для более простого использования в дальнейшем:
```
netsh advfirewall firewall set rule name="OpenSSH SSH Server Preview (sshd)" new name="sshd"
```
! После изменения имени, при удалении OpenSSH с помощью uninstaller-a,
правило файрвола (возможно) останется.

Теперь поменяем порт с 22 на `26969`:
```
netsh advfirewall firewall set rule name="sshd" new localport="26969"
```

И проверим:
```
netsh advfirewall firewall show rule name="sshd"
```

После этого надо не забыть также поменять порт в конфиге `sshd_config`

### Конфигурация sshd_config
Сервер уже остановлен. Файрвол настроен. Откроем sshd_config на редактирование (с админскими привелегиями):
```
C:\ProgramData\ssh\sshd_config
```

Раскоментируем и изменим строки:
```
# Changed from default 22 for better security
# Also don't forget to change firewall rule for new port
Port 26969
```

```
#HostKey __PROGRAMDATA__/ssh/ssh_host_rsa_key
#HostKey __PROGRAMDATA__/ssh/ssh_host_dsa_key
#HostKey __PROGRAMDATA__/ssh/ssh_host_ecdsa_key

# Don't use other algos, only ED25519
HostKey __PROGRAMDATA__/ssh/ssh_host_ed25519_key
```


```
PubkeyAuthentication yes

# Password auth is insecure! Only certs must be used
PasswordAuthentication no
```


Запустим службы:
```
sc start sshd
sc start ssh-agent
```

Проверим что службы запустились (и не пробуют постоянно перезапуститься поймав какую-то ошибку в конфиге):
```
sc queryex sshd
sc queryex ssh-agent
```

Попробуем подключиться к серверу с самого же себя:
```
ssh Admin@localhost -p 26969
```


Добавим ключ клиентской машины в разрешенные ключи в директории пользователя в субдиректории `.ssh\autorized_keys`

A если пользователь является администратором, то в 
`C:\ProgramData\ssh\administrators_authorized_keys` :

По-умолчанию, `administrators_authorized_keys` не существует. Его можно создать.
```powershell
# powershell
cd $env:USERPROFILE\.ssh
cp id_ed25519.pub "$env:programdata\ssh\administrators_authorized_keys"
```
Затем нужно ограничить этому файлу доступ сторонним пользователям и службам. Например, скопировав права доступа из другого файла.
```powershell
# powershell
get-acl "$env:programdata\ssh\ssh_host_ed25519_key" | set-acl "$env:programdata\ssh\administrators_authorized_keys"
```


Можем проверить как работает SSH-сервер. Сперва перезапустив его,
а затем добавив ключ серверной машины в разрешенные ключи и выполнив подключение с самой же серверной машины:

```
cd %USERPROFILE%\.ssh
ssh -i ./id_ed25519 -p 26969 admin@localhost
```

В данном случае, на сервере был запущен `ssh-keygen` и сгенерированы
пользовательские ключи, которые лягли в директорию `.ssh` пользователя.

В `C:\Users\Admin\.ssh\id_ed25519.pub` публичный ключ. Вот так выглядит строка авторизации, которую можно добавить в `.ssh\autorized_keys`в директории пользователя (для простых пользователей), или в
`C:\ProgramData\ssh\administrators_authorized_keys` для администраторов.
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIF+0l+ATKdFmITm8oT69mpmoQJb+Va0K/pusd3/lFzeK admin@DESKTOP-DLSE66G
```

По-хорошему, этот ключ нужно генерировать на гостевой машине и публичную строку просто добавлять в авторизованные ключи на сервере.

Это примерно то же самое, что мы делали для Git и GitHub.

Также можно авторизоваться на удаленном сервере тем же самым ключом,
который хранится в GPG-связке и который можно экспортировать в SSH-формате с помощью команды:
```bash
# bash
$ gpg --export-ssh-key C58C90DB

ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKZVs//45jGtSWd4Fk2sPK/GP7AYY/zCxbisJsCDfS9d openpgp:0xC58C90DB
```


#### Логи сервера
По-умолчанию Windows-порт OpenSSH пишет очень ограниченные логи, при чем
в системный журнал.
Если что-то не получается, можно включить детальный логгинг в конфиге `sshd_server`:
```
# Logging
SyslogFacility LOCAL0
LogLevel DEBUG
```
Затем перезапустить сервер.
И в директории `C:\ProgramData\ssh\logs` будут появляться лог-файлы.
Не стоит включать такой подробный лог надолго, `DEBUG` – только для отладки.


#### Смена командного интерпретатора SSH
Установим Git for Windows. В его комплекте есть отменный bash.

Добавим директорию Git for Windows в PATH.

Затем поменяем ключ реестра, указав интерпретатор команд как bash
для OpenSSH:
```powershell
# powershell
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Program Files\Git\bin\bash.exe" -PropertyType String -Force
```


### Безопасность SSH
Стандартный конфиг не является безопасным. Наш конфиг – хороший.
Но все еще не максимально защищенный от интрузий.

Можно посмотреть hardened-конфиги, например, [тут](https://github.com/k4yt3x/sshd_config/blob/master/sshd_config).

А также использовать одну из утилит для аудита безопасности уже настроенного ssh-сервера, например, [ssh-audit](https://github.com/jtesta/ssh-audit)
```bash
pipx install ssh-audit
```

```bash
$ ssh-audit -p 26969 192.168.90.142
```

    # general
    (gen) banner: SSH-2.0-OpenSSH_for_Windows_9.8 Win32-OpenSSH-GitHub
    (gen) compatibility: OpenSSH 9.6+, Dropbear SSH 2020.79+
    (gen) compression: enabled (zlib@openssh.com)

    # key exchange algorithms
    (kex) curve25519-sha256                     -- [info] available since OpenSSH 7.4, Dropbear SSH 2018.76
                                                `- [info] default key exchange from OpenSSH 7.4 to 8.9
    (kex) curve25519-sha256@libssh.org          -- [info] available since OpenSSH 6.4, Dropbear SSH 2013.62
                                                `- [info] default key exchange from OpenSSH 6.5 to 7.3
    (kex) ecdh-sha2-nistp256                    -- [fail] using elliptic curves that are suspected as being backdoored by the U.S. National Security Agency
                                                `- [info] available since OpenSSH 5.7, Dropbear SSH 2013.62
    (kex) ecdh-sha2-nistp384                    -- [fail] using elliptic curves that are suspected as being backdoored by the U.S. National Security Agency
                                                `- [info] available since OpenSSH 5.7, Dropbear SSH 2013.62
    (kex) ecdh-sha2-nistp521                    -- [fail] using elliptic curves that are suspected as being backdoored by the U.S. National Security Agency
                                                `- [info] available since OpenSSH 5.7, Dropbear SSH 2013.62
    (kex) diffie-hellman-group-exchange-sha256 (3072-bit) -- [info] available since OpenSSH 4.4
                                                        `- [info] OpenSSH's GEX fallback mechanism was triggered during testing. Very old SSH clients will still be able to create connections using a 2048-bit modulus, though modern clients will use 3072. This can only be disabled by recompiling the code (see https://github.com/openssh/openssh-portable/blob/V_9_4/dh.c#L477).
    (kex) diffie-hellman-group16-sha512         -- [info] available since OpenSSH 7.3, Dropbear SSH 2016.73
    (kex) diffie-hellman-group18-sha512         -- [info] available since OpenSSH 7.3
    (kex) diffie-hellman-group14-sha256         -- [warn] 2048-bit modulus only provides 112-bits of symmetric strength
                                                `- [info] available since OpenSSH 7.3, Dropbear SSH 2016.73
    (kex) ext-info-s                            -- [info] available since OpenSSH 9.6
                                                `- [info] pseudo-algorithm that denotes the peer supports RFC8308 extensions
    (kex) kex-strict-s-v00@openssh.com          -- [info] pseudo-algorithm that denotes the peer supports a stricter key exchange method as a counter-measure to the Terrapin attack (CVE-2023-48795)

    # host-key algorithms
    (key) ssh-ed25519                           -- [info] available since OpenSSH 6.5, Dropbear SSH 2020.79

    # encryption algorithms (ciphers)
    (enc) chacha20-poly1305@openssh.com         -- [info] available since OpenSSH 6.5, Dropbear SSH 2020.79
                                                `- [info] default cipher since OpenSSH 6.9
    (enc) aes128-ctr                            -- [info] available since OpenSSH 3.7, Dropbear SSH 0.52
    (enc) aes192-ctr                            -- [info] available since OpenSSH 3.7
    (enc) aes256-ctr                            -- [info] available since OpenSSH 3.7, Dropbear SSH 0.52
    (enc) aes128-gcm@openssh.com                -- [info] available since OpenSSH 6.2
    (enc) aes256-gcm@openssh.com                -- [info] available since OpenSSH 6.2

    # message authentication code algorithms
    (mac) umac-64-etm@openssh.com               -- [warn] using small 64-bit tag size
                                                `- [info] available since OpenSSH 6.2
    (mac) umac-128-etm@openssh.com              -- [info] available since OpenSSH 6.2
    (mac) hmac-sha2-256-etm@openssh.com         -- [info] available since OpenSSH 6.2
    (mac) hmac-sha2-512-etm@openssh.com         -- [info] available since OpenSSH 6.2
    (mac) umac-64@openssh.com                   -- [warn] using encrypt-and-MAC mode
                                                `- [warn] using small 64-bit tag size
                                                `- [info] available since OpenSSH 4.7
    (mac) umac-128@openssh.com                  -- [warn] using encrypt-and-MAC mode
                                                `- [info] available since OpenSSH 6.2
    (mac) hmac-sha2-256                         -- [warn] using encrypt-and-MAC mode
                                                `- [info] available since OpenSSH 5.9, Dropbear SSH 2013.56
    (mac) hmac-sha2-512                         -- [warn] using encrypt-and-MAC mode
                                                `- [info] available since OpenSSH 5.9, Dropbear SSH 2013.56

    # fingerprints
    (fin) ssh-ed25519: SHA256:AAAAC3NzaC1lZDI1NTE5AAAAIKZVs//45jGtSWd4Fk2sPK/GP7AYY/zCxbisJsCDfS9d

    # additional info
    (nfo) Be aware that, while this target properly supports the strict key exchange method (via the kex-strict-?-v00@openssh.com marker) needed to protect against the Terrapin vulnerability (CVE-2023-48795), all peers must also support this feature as well, otherwise the vulnerability will still be present.  The following algorithms would allow an unpatched peer to create vulnerable SSH channels with this target: chacha20-poly1305@openssh.com.  If any CBC ciphers are in this list, you may remove them while leaving the *-etm@openssh.com MACs in place; these MACs are fine while paired with non-CBC cipher types.


```bash
$ ssh-audit -p 26969 192.168.90.142 -P "Hardened Ubuntu Server 24.04 LTS (version 1)"
```

    Host:   192.168.90.142:26969
    Policy: Hardened Ubuntu Server 24.04 LTS (version 1)
    Result: ❌ Failed!

    Errors:
    * Ciphers did not match.
        - Expected: chacha20-poly1305@openssh.com, aes256-gcm@openssh.com, aes256-ctr, aes192-ctr, aes128-gcm@openssh.com, aes128-ctr
        - Actual:   chacha20-poly1305@openssh.com, aes128-ctr, aes192-ctr, aes256-ctr, aes128-gcm@openssh.com, aes256-gcm@openssh.com

    * Host keys did not match.
        - Expected (required; exact match): ssh-ed25519, rsa-sha2-512, rsa-sha2-256
        - Expected (optional): sk-ssh-ed25519@openssh.com, ssh-ed25519-cert-v01@openssh.com, sk-ssh-ed25519-cert-v01@openssh.com, rsa-sha2-256-cert-v01@openssh.com, rsa-sha2-512-cert-v01@openssh.com
        - Actual:              ssh-ed25519

    * Key exchanges did not match.
        - Expected: sntrup761x25519-sha512@openssh.com, curve25519-sha256, curve25519-sha256@libssh.org, diffie-hellman-group18-sha512, diffie-hellman-group-exchange-sha256, diffie-hellman-group16-sha512, ext-info-s, kex-strict-s-v00@openssh.com
        - Actual:   curve25519-sha256, curve25519-sha256@libssh.org, ecdh-sha2-nistp256, ecdh-sha2-nistp384, ecdh-sha2-nistp521, diffie-hellman-group-exchange-sha256, diffie-hellman-group16-sha512, diffie-hellman-group18-sha512, diffie-hellman-group14-sha256, ext-info-s, kex-strict-s-v00@openssh.com

    * MACs did not match.
        - Expected: hmac-sha2-512-etm@openssh.com, hmac-sha2-256-etm@openssh.com, umac-128-etm@openssh.com
        - Actual:   umac-64-etm@openssh.com, umac-128-etm@openssh.com, hmac-sha2-256-etm@openssh.com, hmac-sha2-512-etm@openssh.com, umac-64@openssh.com, umac-128@openssh.com, hmac-sha2-256, hmac-sha2-512
