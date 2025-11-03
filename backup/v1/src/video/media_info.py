"""
Media information helpers using mediainfo CLI when available.
"""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)


def _has_mediainfo() -> bool:
    return shutil.which("mediainfo") is not None


def probe_media_info(input_file: str | Path) -> Dict[str, str]:
    """
    Return a subset of media info fields using mediainfo CLI.

    Args:
        input_file: path to media file (mkv/mp4)

    Returns:
        Dict with keys: size, duration, video_bitrate, video_codec,
        resolution, fps, audio_bitrate, audio_channels, audio_codec, sampling
    """
    path = Path(input_file)
    result: Dict[str, str] = {}
    if not path.exists():
        return result

    if not _has_mediainfo():
        logger.warning("mediainfo CLI non trouvé - champs NFO réduits")
        try:
            stat = path.stat()
            result["size"] = f"{stat.st_size} B"
        except (OSError, PermissionError) as e:
            logger.debug(f"Erreur récupération taille fichier: {e}")
            pass
        return result

    def run(fmt: str) -> str:
        try:
            out = subprocess.check_output(
                ["mediainfo", f"--Inform={fmt}", str(path)],
                stderr=subprocess.DEVNULL,
            )
            return out.decode("utf-8", errors="ignore").strip()
        except subprocess.CalledProcessError:
            return ""

    result["size"] = run("General;%FileSize/String3%")
    result["duration"] = run("General;%Duration/String%")
    result["video_bitrate"] = run("Video;%BitRate/String%")
    result["video_codec"] = run("Video;%Encoded_Library_Name%") or run("Video;%Format%")
    result["resolution"] = run("Video;%Width%x%Height%")
    result["fps"] = run("Video;%FrameRate%")
    result["audio_bitrate"] = run("Audio;%BitRate/String%")
    result["audio_channels"] = run("Audio;%Channel(s)%")
    result["audio_codec"] = run("Audio;%Format%")
    result["sampling"] = run("Audio;%SamplingRate/String%")

    # Normalize a few fields similar to batch script
    if result.get("video_codec"):
        result["codecID"] = "x264" if result["video_codec"].strip() else "H264"
    if result.get("audio_codec"):
        ac = result["audio_codec"].upper()
        mapping = {"AC-3": "AC3", "E-AC-3": "E-AC3", "MPEG AUDIO": "MP2", "AAC": "AAC"}
        result["audio_codec_norm"] = (
            mapping.get(ac, result["audio_codec"]) if ac else result["audio_codec"]
        )
    if result.get("audio_channels"):
        ch = result["audio_channels"].strip()
        if ch == "6":
            result["audio_channels_norm"] = "5.1"
        elif ch == "2":
            result["audio_channels_norm"] = "2.0"
        elif ch == "1":
            result["audio_channels_norm"] = "1.0"
        else:
            result["audio_channels_norm"] = ch

    return result
