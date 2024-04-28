import spotipy
import yandex_music
from requests import ReadTimeout
import argparse
import time


def ym_login_with_token(token):
    """Авторизация в Яндекс Музыке с помощью токена.
    Требуется токен Яндекс Музыки.
    Способы получения токена указаны в README.md.
    Возвращает объект клиента Яндекс Музыки."""

    print("Yandex Music authorization: ", end="")

    t1 = time.time()
    client = yandex_music.Client(token).init()
    if client:
        print(f"successful, time taken: {time.time() - t1:.2f} seconds\n")
        return client
    else:
        print("failed\n")
        return


def ym_get_liked_tracks(client):
    """Получение треков, лайкнутых пользователем в Яндекс Музыке.
    Принимает объект клиента Яндекс Музыки.
    Возвращает список треков в формате 'Исполнитель - Название трека'"""

    print("Fetching liked tracks from Yandex Music: ", end="")

    t1 = time.time()
    like_tracks = client.users_likes_tracks()
    if like_tracks:
        while like_tracks:
            like_track = like_tracks.fetch_tracks()
            print(
                f"successful, {len(like_track)} liked tracks from Yandex Music, time taken: {time.time() - t1:.2f} seconds\n"
            )
            return [f"{track.artists[0].name} - {track.title}" for track in like_track]
    else:
        print("failed\n")
        return


def sp_auth(username, client_id, client_secret):
    """Авторизация в Spotify.
    Принимает имя пользователя Spotify, client_id и client_secret от OAuth приложения Spotify.
    Инструкция по созданию приложения и получению client_id и client_secret указаны в README.md.
    Возвращает объект клиента Spotify."""

    print("Spotify authorization: ", end="")
    scope = "playlist-modify-public"
    return spotipy.Spotify(
        auth_manager=spotipy.SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:8888/callback",
            scope=scope,
            username=username,
        ),
        retries=5,
        requests_timeout=5,
    )


def sp_create_playlist(sp, username, playlist_name):
    """Создание плейлиста с лайкнутыми треками из Яндекс Музыки в Spotify.
    Принимает объект клиента Spotify, имя пользователя Spotify и название плейлиста.
    Возвращает ID созданного плейлиста."""

    user_id = sp.me()["id"]
    if user_id:
        print("successful\n")
    else:
        print("failed\n")
        return

    print("Creating playlist in Spotify: ", end="")

    t1 = time.time()
    playlist = sp.user_playlist_create(user_id, playlist_name)
    if playlist:
        print(f"successful, time taken: {time.time() - t1:.2f} seconds\n")
        return playlist["id"]
    else:
        print("failed\n")
        return


def sp_add_tracks(sp, playlist_id, tracks):
    """Добавление лайкнутых треков из Яндекс Музыки в Spotify.
    Принимает объект клиента Spotify, ID созданного в методе sp_create_playlist плейлиста Spotify и список треков из ym_get_liked_tracks.
    Логирует ошибки добавления треков в плейлист, если они возникли. Успешные добавления не логируются."""

    print("Adding liked tracks to Spotify playlist")

    t1 = time.time()
    bunch = []
    counter = 0
    for track in tracks:
        track = track.split(" - ")
        query = f"artist:{track[0]} track:{track[1]}"
        try:
            result = sp.search(query, type="track")
            if result["tracks"]["items"]:
                if (len(bunch) == 100):  # 100 - максимальное количество треков, которое можно добавить в плейлист за один запрос. Не увеличивайте это число во избежание ошибок.
                    sp.playlist_add_items(playlist_id, bunch)
                    print("Added a bunch of 100 tracks to the playlist")
                    counter += 100
                    bunch.clear()
                else:
                    bunch.append(result["tracks"]["items"][0]["uri"])
            else:
                print(f"Failed to add {track[0]} - {track[1]} to Spotify playlist. Time: {time.time() - t1:.2f} seconds")
        except Exception as e:
            if isinstance(e, TimeoutError):
                print(f"Failed to add {track[0]} - {track[1]} to Spotify playlist, TimeoutError exception occured. Time: {time.time() - t1:.2f} seconds")
            elif isinstance(e, ReadTimeout):
                print(f"Seems like your internet connection is down, ReadTimeout exception occured. Failed to add {track[0]} - {track[1]} to Spotify playlist. Time: {time.time() - t1:.2f} seconds")
            else:
                print(f"Failed to add {track[0]} - {track[1]} to Spotify playlist, unknown exception occured. Time: {time.time() - t1:.2f} seconds")

    if bunch:
        counter += len(bunch)
        sp.playlist_add_items(playlist_id, bunch)

    print(f"Added {counter} founded liked tracks to Spotify playlist, time taken: {time.time() - t1:.2f} seconds\n")


def main():
    """Основная функция.
    Парсит аргументы командной строки, такие как токены Яндекс Музыки и Spotify, имя пользователя Spotify и название плейлиста.
    Запускает авторизацию в Яндекс Музыке и Spotify, получение лайкнутых треков из Яндекс Музыки, создание плейлиста в Spotify и добавление треков в плейлист."""

    parser = argparse.ArgumentParser(
        description="Transfer liked tracks from Yandex Music to Spotify"
    )

    parser.add_argument(
        "--ymtoken", 
        required=True, 
        help="Token for Yandex Music authorization"
    )

    parser.add_argument(
        "--spclientid", 
        required=True, 
        help="Client ID for Spotify authorization"
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

    t1 = time.time()

    ym_client = ym_login_with_token(ym_token)
    tracks = ym_get_liked_tracks(ym_client)
    sp = sp_auth(sp_username, sp_client_id, sp_client_secret)
    playlist_id = sp_create_playlist(sp, sp_username, playlist_name)
    sp_add_tracks(sp, playlist_id, tracks)

    print(f"Finished, total time taken: {time.time() - t1:.2f} seconds")


if __name__ == "__main__":
    main()
