import spotipy
import yandex_music
import argparse


def ym_login_with_token(token):
    """Авторизация в Яндекс Музыке с помощью токена.
    Требуется токен Яндекс Музыки.
    Способы получения токена указаны в README.md.
    Возвращает объект клиента Яндекс Музыки."""

    print("Yandex Music authorization")
    client = yandex_music.Client(token).init()
    if client:
        print("Yandex Music authorization successful\n")
        return client
    else:
        print("Yandex Music authorization failed\n")
        return


def ym_get_liked_tracks(client):
    """Получение треков, лайкнутых пользователем в Яндекс Музыке.
    Принимает объект клиента Яндекс Музыки.
    Возвращает список треков в формате 'Исполнитель - Название трека'"""

    print("Fetching liked tracks from Yandex Music")
    like_tracks = client.users_likes_tracks()
    if like_tracks:
        while like_tracks:
            like_track = like_tracks.fetch_tracks()
            print(f"Fetched {len(like_track)} liked tracks from Yandex Music")
            return [f"{track.artists[0].name} - {track.title}" for track in like_track]
    else:
        print("Failed to fetch liked tracks from Yandex Music\n")
        return


def sp_auth(username, client_id, client_secret):
    """Авторизация в Spotify.
    Принимает имя пользователя Spotify, client_id и client_secret от OAuth приложения Spotify.
    Инструкция по созданию приложения и получению client_id и client_secret указаны в README.md.
    Возвращает объект клиента Spotify."""

    print("Spotify authorization")
    scope = "playlist-modify-public"
    return spotipy.Spotify(
        auth_manager=spotipy.SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:8888/callback",
            scope=scope,
            username=username,
        )
    )


def sp_create_playlist(sp, username, playlist_name):
    """Создание плейлиста с лайкнутыми треками из Яндекс Музыки в Spotify.
    Принимает объект клиента Spotify, имя пользователя Spotify и название плейлиста.
    Возвращает ID созданного плейлиста."""

    print("Creating playlist in Spotify")
    user_id = sp.me()["id"]
    playlist = sp.user_playlist_create(user_id, playlist_name)
    if playlist:
        print("Created playlist in Spotify\n")
        return playlist["id"]
    else:
        print("Failed to create playlist in Spotify")
        return


def sp_add_tracks(sp, playlist_id, tracks):
    """Добавление лайкнутых треков из Яндекс Музыки в Spotify.
    Принимает объект клиента Spotify, ID созданного в методе sp_create_playlist плейлиста Spotify и список треков из ym_get_liked_tracks.
    Логирует ошибки добавления треков в плейлист, если они возникли. Успешные добавления не логируются. Пропускает ошибки TimeoutError."""

    print("Adding liked tracks to Spotify playlist")
    for track in tracks:
        track = track.split(" - ")
        query = f"artist:{track[0]} track:{track[1]}"
        result = sp.search(query, type="track")
        if result["tracks"]["items"]:
            sp.playlist_add_items(playlist_id, [result["tracks"]["items"][0]["uri"]])
        else:
            print(f"Failed to add {track[0]} - {track[1]} to Spotify playlist")
        if TimeoutError:
            pass
    print("Added liked tracks to Spotify playlist\n\nDone")


def main():
    """Основная функция.
    Парсит аргументы командной строки, такие как токены Яндекс Музыки и Spotify, имя пользователя Spotify и название плейлиста.
    Запускает авторизацию в Яндекс Музыке и Spotify, получение лайкнутых треков из Яндекс Музыки, создание плейлиста в Spotify и добавление треков в плейлист."""

    parser = argparse.ArgumentParser(
        description="Transfer liked tracks from Yandex Music to Spotify"
    )

    parser.add_argument(
        "--ymtoken", required=True, help="Token for Yandex Music authorization"
    )

    parser.add_argument(
        "--spclientid", required=True, help="Client ID for Spotify authorization"
    )
    parser.add_argument(
        "--spclientsecret",
        required=True,
        help="Client secret for Spotify authorization",
    )
    parser.add_argument(
        "--spusername", required=True, help="Username for Spotify authorization"
    )

    parser.add_argument(
        "--playlistname",
        default="Liked from Yandex Music",
        help="Name for the playlist in Spotify",
    )

    args = parser.parse_args()

    ym_token = args.ymtoken
    sp_client_id = args.spclientid
    sp_client_secret = args.spclientsecret
    sp_username = args.spusername
    playlist_name = args.playlistname

    print("\nStarting\n")

    ym_client = ym_login_with_token(ym_token)
    tracks = ym_get_liked_tracks(ym_client)
    sp = sp_auth(sp_username, sp_client_id, sp_client_secret)
    playlist_id = sp_create_playlist(sp, sp_username, playlist_name)
    sp_add_tracks(sp, playlist_id, tracks)


if __name__ == "__main__":
    main()
