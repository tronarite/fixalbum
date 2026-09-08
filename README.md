# fixalbum

`fix_album_artist.py` — normaliza la etiqueta **Album Artist** en bibliotecas de
música para que [Navidrome](https://www.navidrome.org/) (u otros servidores que
agrupan álbumes por Album Artist) no parta un álbum en varios cuando algunas
pistas tienen colaboradores.

## Qué hace

Recorre la biblioteca **carpeta a carpeta** (una carpeta = un álbum). En cada
carpeta:

1. Lee `Artist`, `Album Artist` y `Album` de cada `.mp3` / `.flac`.
2. Si **al menos una** pista tiene varios artistas —separados por `,` `/` `&`
   ` feat. ` o ` con `— detecta el artista principal (el primero de cada pista,
   el más repetido del álbum).
3. Escribe ese artista como `Album Artist` (`TPE2` en MP3, `albumartist` en FLAC)
   en **todas** las pistas del álbum que no lo tengan ya.

Los álbumes sin ningún colaborador se dejan intactos.

## Uso

```bash
pip install mutagen

python fix_album_artist.py "D:\Musica"            # aplica los cambios
python fix_album_artist.py "D:\Musica" --dry-run  # solo simula, no toca nada
```

Después haz un **rescan completo** en Navidrome para que recoja los cambios.

## Requisitos

- Python 3
- [`mutagen`](https://mutagen.readthedocs.io/)
