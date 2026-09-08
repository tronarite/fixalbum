#!/usr/bin/env python3
"""
fix_album_artist.py
-------------------
Recorre tu librería de música carpeta a carpeta (= álbum a álbum).
Para cada carpeta detecta el artista principal (el más repetido) y lo
pone como Album Artist en TODAS las canciones del álbum, aunque no
tengan colaboradores.

Uso:
    python fix_album_artist.py "G:\\Música\\MP3"
    python fix_album_artist.py "G:\\Música\\MP3" --dry-run

Dependencias:
    pip install mutagen
"""

import os
import sys
import re
import argparse
from collections import Counter
from mutagen.mp3 import MP3
from mutagen.id3 import TPE2
from mutagen.flac import FLAC

SEPARATORS_RE = re.compile(r",|/| & | feat\.? | con ", re.IGNORECASE)


def get_first_artist(artist_str: str) -> str:
    return SEPARATORS_RE.split(artist_str)[0].strip()


def read_tags_mp3(filepath):
    try:
        audio = MP3(filepath)
        tags = audio.tags
        if tags is None:
            return None
        artist_tag = tags.get("TPE1")
        album_artist_tag = tags.get("TPE2")
        album_tag = tags.get("TALB")
        artist = str(artist_tag.text[0]).strip() if artist_tag and artist_tag.text else ""
        album_artist = str(album_artist_tag.text[0]).strip() if album_artist_tag and album_artist_tag.text else ""
        album = str(album_tag.text[0]).strip() if album_tag and album_tag.text else ""
        return artist, album_artist, album
    except Exception:
        return None


def read_tags_flac(filepath):
    try:
        audio = FLAC(filepath)
        artist = audio.get("artist", [""])[0].strip()
        album_artist = audio.get("albumartist", [""])[0].strip()
        album = audio.get("album", [""])[0].strip()
        return artist, album_artist, album
    except Exception:
        return None


def write_album_artist_mp3(filepath, album_artist, dry_run):
    try:
        audio = MP3(filepath)
        if audio.tags is None:
            return False
        if not dry_run:
            audio.tags["TPE2"] = TPE2(encoding=3, text=album_artist)
            audio.save()
        return True
    except Exception as e:
        print(f"  [ERROR] {filepath}: {e}")
        return False


def write_album_artist_flac(filepath, album_artist, dry_run):
    try:
        audio = FLAC(filepath)
        if not dry_run:
            audio["albumartist"] = [album_artist]
            audio.save()
        return True
    except Exception as e:
        print(f"  [ERROR] {filepath}: {e}")
        return False


def process_folder(folder, dry_run):
    files_info = []

    for filename in sorted(os.listdir(folder)):
        filepath = os.path.join(folder, filename)
        ext = filename.lower().rsplit(".", 1)[-1]
        if ext == "mp3":
            tags = read_tags_mp3(filepath)
        elif ext == "flac":
            tags = read_tags_flac(filepath)
        else:
            continue
        if tags is None:
            continue
        artist, album_artist, album = tags
        files_info.append((filepath, ext, artist, album_artist, album))

    if not files_info:
        return 0

    # Solo actuar si hay al menos una cancion con colaboradores
    has_collab = any(SEPARATORS_RE.search(f[2]) for f in files_info if f[2])
    if not has_collab:
        return 0

    first_artists = [get_first_artist(f[2]) for f in files_info if f[2]]
    if not first_artists:
        return 0

    main_artist = Counter(first_artists).most_common(1)[0][0]

    all_ok = all(f[3] == main_artist for f in files_info)
    if all_ok:
        return 0

    print(f"\n📁 {os.path.basename(folder)}")
    print(f"   Artista principal detectado: {main_artist}")

    changed = 0
    for filepath, ext, artist, album_artist, album in files_info:
        if album_artist == main_artist:
            continue
        filename = os.path.basename(filepath)
        print(f"   {'[SIM]' if dry_run else '[OK] '} {filename}")
        print(f"         Artist:       {artist}")
        print(f"         Album Artist: '{album_artist}' → '{main_artist}'")

        if ext == "mp3":
            ok = write_album_artist_mp3(filepath, main_artist, dry_run)
        else:
            ok = write_album_artist_flac(filepath, main_artist, dry_run)
        if ok:
            changed += 1

    return changed


def process_library(music_dir, dry_run):
    total_changed = 0
    total_albums = 0

    for root, dirs, files in os.walk(music_dir):
        dirs.sort()
        changed = process_folder(root, dry_run)
        if changed:
            total_changed += changed
            total_albums += 1

    print("\n" + "=" * 50)
    if dry_run:
        print("MODO SIMULACIÓN — no se ha modificado nada.")
    print(f"Archivos modificados: {total_changed}")
    print(f"Álbumes afectados:    {total_albums}")
    if not dry_run and total_changed > 0:
        print("\n✓ Haz un rescan completo en Navidrome para aplicar los cambios.")


def main():
    parser = argparse.ArgumentParser(
        description="Arregla Album Artist en MP3/FLAC para Navidrome (por carpeta)."
    )
    parser.add_argument("music_dir", help="Ruta a tu carpeta de música")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simula sin modificar nada")
    args = parser.parse_args()

    if not os.path.isdir(args.music_dir):
        print(f"Error: '{args.music_dir}' no existe.")
        sys.exit(1)

    mode = "SIMULACIÓN (--dry-run)" if args.dry_run else "REAL"
    print(f"Modo: {mode}")
    print(f"Carpeta: {args.music_dir}")
    print("=" * 50)

    process_library(args.music_dir, args.dry_run)


if __name__ == "__main__":
    main()

