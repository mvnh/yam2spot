# yam2spot
Скрипт для переноса лайкнутых треков из аккаунта Яндекс Музыки в аккаунт Spotify

## Настройка
Установите необходимые зависимости:
```bash
pip3 install -r requirements.txt
```

Получите токен от вашего аккаунта в Яндекс Музыке:
* Расширения для [Google Chrome](https://chromewebstore.google.com/detail/yandex-music-token/lcbjeookjibfhjjopieifgjnhlegmkib) и [Mozilla Firefox](https://addons.mozilla.org/en-US/firefox/addon/yandex-music-token/)
* [Приложение для ОС Android](https://github.com/MarshalX/yandex-music-token)

[Создайте OAuth Spotify приложение](https://developer.spotify.com/dashboard):
* Нажмите **Create app**
* Заполните обязательные поля
* В **Redirect URIs** впишите **http://localhost:8888/callback**

## Использование
1. Получите токен вашего аккаунта в Яндекс Музыке
1. В настройках созданного OAuth приложения скопируйте **Client ID** и **Client secret**
2. Запустите следующую команду в командной строке, предварительно подставив полученные значения:
```bash
py -m yam2spot --ymtoken <yandex_music_token> --spclientid <spotify_client_id> --spclientsecret <client_secret_spotify> --spusername <spotify_account_username> --playlistname <название_плейлиста>
```
Аргумент `--playlistname` не является обязательным. Дефолтным значением является "Liked from Yandex Music"