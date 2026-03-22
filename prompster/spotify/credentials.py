from enum import StrEnum

from pydantic_settings import BaseSettings


class _SpotifyScope(StrEnum):
    USER_READ_PRIVATE = "user-read-private"
    PLAYLIST_READ_PRIVATE = "playlist-read-private"
    PLAYLIST_MODIFY_PUBLIC = "playlist-modify-public"
    PLAYLIST_MODIFY_PRIVATE = "playlist-modify-private"


SPOTIFY_SCOPES = " ".join(
    [
        _SpotifyScope.USER_READ_PRIVATE,
        _SpotifyScope.PLAYLIST_READ_PRIVATE,
        _SpotifyScope.PLAYLIST_MODIFY_PUBLIC,
        _SpotifyScope.PLAYLIST_MODIFY_PRIVATE,
    ]
)


class SpotifyCredentials(BaseSettings):
    spotify_client_id: str
    spotify_client_secret: str
    spotify_redirect_uri: str = "http://127.0.0.1:8080"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }
