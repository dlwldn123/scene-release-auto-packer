#!/usr/bin/env python3
"""
TV/Video packer: sample creation (mkvmerge), RAR volumes, SFV, NFO.
"""

import argparse
import datetime as dt
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

from src.packaging.rar import create_rar_volumes
from src.packaging.sfv import generate_sfv

from .media_info import probe_media_info

logger = logging.getLogger(__name__)


def _guess_profile(release_name: str) -> Tuple[str, int, int]:
    name = release_name.upper()
    # Defaults
    res = "sd"
    crf = 19
    rarsize = 20
    mapping = [
        ("FRENCH.HDTV", ("sd", 19, 20)),
        ("FRENCH.720P.HDTV", ("hd", 18, 50)),
        ("FRENCH.1080P.HDTV", ("hd", 17, 50)),
        ("FRENCH.WEB", ("sd", 19, 20)),
        ("FRENCH.720P.WEB", ("hd", 18, 50)),
        ("FRENCH.1080P.WEB", ("hd", 17, 50)),
        ("MULTI.1080P.WEB", ("hd", 17, 50)),
    ]
    for key, vals in mapping:
        if key in name:
            res, crf, rarsize = vals
            break
    return res, crf, rarsize


def _has_mkvmerge() -> bool:
    return shutil.which("mkvmerge") is not None


def create_sample(
    input_mkv: Path, sample_dir: Path, base_name: str, duration: str = "00:01:00"
) -> Optional[Path]:
    sample_dir.mkdir(parents=True, exist_ok=True)
    sample_path = sample_dir / f"{base_name}-sample.mkv"
    if _has_mkvmerge():
        try:
            subprocess.check_call(
                [
                    "mkvmerge",
                    "-o",
                    str(sample_path),
                    "(",
                    str(input_mkv),
                    ")",
                    "--split",
                    f"parts:00:00:00-{duration}",
                ]
            )
            return sample_path
        except subprocess.CalledProcessError as e:
            logger.warning(f"mkvmerge échec: {e}")
    # Fallback: copy full file
    shutil.copy2(input_mkv, sample_path)
    return sample_path


def generate_tv_nfo(
    release_dir: Path,
    release_name: str,
    link: Optional[str],
    media: Dict[str, str],
    crf: int,
    rarsize: int,
    rar_count: int,
    tv_metadata: Optional[Dict[str, str]] = None,
) -> Path:
    nfo_path = release_dir / f"{release_name}.nfo"
    date_str = dt.date.today().isoformat()
    lines = []
    lines.append("")
    lines.append(
        "+-----------------------------------------------------------------------+"
    )
    lines.append("")

    # Titre enrichi si disponible
    if tv_metadata and tv_metadata.get("title"):
        lines.append(f"\t{release_name}")
        lines.append("")
        lines.append(f"\tTitle          : {tv_metadata.get('title')}")
        if tv_metadata.get("episode_title"):
            lines.append(f"\tEpisode Title  : {tv_metadata.get('episode_title')}")
        if tv_metadata.get("year"):
            lines.append(f"\tYear           : {tv_metadata.get('year')}")
        if tv_metadata.get("plot") or tv_metadata.get("episode_plot"):
            plot = tv_metadata.get("episode_plot") or tv_metadata.get("plot")
            if plot:
                # Tronquer si trop long (max 500 caractères)
                if len(plot) > 500:
                    plot = plot[:497] + "..."
                lines.append(f"\tPlot           : {plot}")
        if tv_metadata.get("rating"):
            lines.append(f"\tRating         : {tv_metadata.get('rating')}/10")
        if tv_metadata.get("genre"):
            lines.append(f"\tGenre          : {tv_metadata.get('genre')}")
        if tv_metadata.get("network"):
            lines.append(f"\tNetwork        : {tv_metadata.get('network')}")
        lines.append("")
    else:
        lines.append(f"\t{release_name}")
        lines.append("")

    lines.append(f"\tRelease date   : {date_str}")
    lines.append("")
    lines.append(f"\tVideo          : {media.get('codecID','H264')} - CRF {crf}")
    lines.append(f"\tBitrate        : {media.get('video_bitrate','N/A')}")
    lines.append(f"\tResolution     : {media.get('resolution','N/A')}")
    lines.append(f"\tFrame rate     : {media.get('fps','N/A')} fps")
    lines.append("")
    lines.append(
        f"\tAudio          : {media.get('audio_codec_norm', media.get('audio_codec','N/A'))} {media.get('audio_channels_norm', media.get('audio_channels',''))}"
    )
    lines.append(f"\tBit rate       : {media.get('audio_bitrate','N/A')}")
    lines.append(f"\tSampling rate  : {media.get('sampling','N/A')}")
    lines.append(f"\tDuration       : {media.get('duration','N/A')}")
    lines.append(f"\tSize           : {media.get('size','N/A')}")
    lines.append(f"\tPackage        : {rar_count} x {rarsize} Mo")
    lines.append("")
    if link:
        lines.append(f"\tLink: {link}")
        lines.append("")
    lines.append(
        "+-----------------------------------------------------------------------+"
    )
    lines.append("")
    content = "\n".join(lines) + "\n"
    with open(nfo_path, "w", encoding="utf-8") as f:
        f.write(content)
    return nfo_path


def pack_tv_release(
    input_mkv: str | Path,
    release_name: str,
    link: Optional[str] = None,
    profile: Optional[str] = None,
    tv_metadata: Optional[Dict[str, str]] = None,
) -> Path:
    input_mkv = Path(input_mkv)
    if not input_mkv.exists():
        raise FileNotFoundError(input_mkv)

    # Setup directories
    release_dir = Path("releases") / release_name
    release_dir.mkdir(parents=True, exist_ok=True)
    sample_dir = release_dir / "Sample"

    # Create sample
    base_name = input_mkv.stem
    create_sample(input_mkv, sample_dir, base_name)

    # Profile selection
    if profile:
        p = profile.upper()
        mapping = {
            "HDTV_SD": ("sd", 19, 20),
            "HDTV_720P": ("hd", 18, 50),
            "HDTV_1080P": ("hd", 17, 50),
            "WEB_SD": ("sd", 19, 20),
            "WEB_720P": ("hd", 18, 50),
            "WEB_1080P": ("hd", 17, 50),
        }
        res, crf, rarsize = mapping.get(p, _guess_profile(release_name))
    else:
        res, crf, rarsize = _guess_profile(release_name)

    # RAR volumes (store method 0, volume size per rarsize)
    # Use our rar helper (method configurable); volume size MB
    rar_output_dir = release_dir
    rar_files = create_rar_volumes(
        filepath=input_mkv,
        output_dir=rar_output_dir,
        volume_size_mb=rarsize,
        method=0,
    )

    # SFV for created files
    generate_sfv(release_name, release_dir)

    # Media info and NFO
    media = probe_media_info(input_mkv)
    generate_tv_nfo(
        release_dir,
        release_name,
        link,
        media,
        crf,
        rarsize,
        rar_count=len(rar_files),
        tv_metadata=tv_metadata,
    )

    return release_dir


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Scene Packer - TV/Video")
    parser.add_argument("input", help="Fichier vidéo source (MKV)")
    parser.add_argument(
        "-r", "--release", required=True, help="Nom de la release (dossier)"
    )
    parser.add_argument("-l", "--link", default=None, help="Lien (optionnel)")
    args = parser.parse_args()

    out = pack_tv_release(args.input, args.release, link=args.link)
    print(str(out))


if __name__ == "__main__":
    main()
