"""
用 ffmpeg 将铜仁实景图片合成一支宣传短片（零成本，不依赖外部视频素材）

输出：static/video/tongren-promo.mp4 （1280x720，约 22 秒，无音轨）

用法：
  python tools/make_promo_video.py
"""
import os
import subprocess
import sys

import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(os.path.dirname(ROOT), "tongren-miniapp", "static", "img")
OUT_DIR = os.path.join(ROOT, "static", "video")
TMP_DIR = os.path.join(ROOT, "static", "video", "_tmp")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FONT = "C\\:/Windows/Fonts/msyhbd.ttc"

# (图片, 字幕标题, 字幕副标题, 缩放方向)
SHOTS = [
    ("fanjingshan.jpg", "梵净山", "云海之上 · 天空之城", "in"),
    ("miaowangcheng.jpg", "苗王城", "千年苗寨 · 银光成诗", "out"),
    ("shiqian-spring.jpg", "石阡温泉", "千年汤泉 · 泡去风尘", "in"),
    ("zhongnanmen.jpg", "中南门古城", "一街灯火 · 半城烟火", "out"),
    ("jinjiang-night.jpg", "锦江夜色", "大美铜仁 · 山水相逢", "in"),
]

CLIP_SEC = 5.0
FADE = 0.6
W, H = 1280, 720
FPS = 30


def run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr[-2000:])
        raise SystemExit("ffmpeg 失败: " + " ".join(args[:6]))
    return p


def make_clip(idx, img, direction):
    src = os.path.join(IMG_DIR, img)
    if not os.path.exists(src):
        raise SystemExit(f"缺少图片: {src}")
    dst = os.path.join(TMP_DIR, f"clip{idx}.mp4")

    if direction == "in":
        zexpr = "min(zoom+0.0016,1.30)"
    else:
        zexpr = "if(lte(zoom,1.0),1.30,max(1.001,zoom-0.0016))"

    vf = (
        f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,"
        f"crop={W * 2}:{H * 2},"
        f"zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={int(CLIP_SEC * FPS)}:s={W}x{H}:fps={FPS},"
        f"format=yuv420p"
    )
    run([
        FFMPEG, "-y", "-loop", "1", "-i", src,
        "-vf", vf, "-t", str(CLIP_SEC),
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-movflags", "+faststart", dst,
    ])
    return dst


def concat(clips):
    args = [FFMPEG, "-y"]
    for c in clips:
        args += ["-i", c]

    parts = []
    last = "[0]"
    for i in range(1, len(clips)):
        offset = CLIP_SEC * i - FADE * i
        out = f"[v{i}]"
        parts.append(
            f"{last}[{i}]xfade=transition=fade:duration={FADE}:offset={offset:.2f}{out}"
        )
        last = out
    fc = ";".join(parts)

    dst = os.path.join(TMP_DIR, "joined.mp4")
    run(args + ["-filter_complex", fc, "-map", last,
                "-c:v", "libx264", "-preset", "medium", "-crf", "22",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", dst])
    return dst


def add_captions(src, clips_count):
    filters = []
    for i, (_, title, sub, _) in enumerate(SHOTS):
        start = max(0.0, CLIP_SEC * i - FADE * i) + 0.35
        end = start + CLIP_SEC - FADE - 0.5
        # 主标题
        filters.append(
            f"drawtext=fontfile='{FONT}':text='{title}':"
            f"fontsize=54:fontcolor=white:borderw=3:bordercolor=black@0.35:"
            f"x=(w-text_w)/2:y=h*0.62:"
            f"enable='between(t,{start:.2f},{end:.2f})'"
        )
        # 副标题
        filters.append(
            f"drawtext=fontfile='{FONT}':text='{sub}':"
            f"fontsize=28:fontcolor=0xF2F6EE:borderw=2:bordercolor=black@0.30:"
            f"x=(w-text_w)/2:y=h*0.62+72:"
            f"enable='between(t,{start + 0.15:.2f},{end:.2f})'"
        )

    dst = os.path.join(OUT_DIR, "tongren-promo.mp4")
    run([FFMPEG, "-y", "-i", src,
         "-vf", ",".join(filters),
         "-c:v", "libx264", "-preset", "medium", "-crf", "23",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", dst])
    return dst


def main():
    print("=" * 56)
    print(" 合成铜仁宣传短片")
    print("=" * 56)
    clips = []
    for i, shot in enumerate(SHOTS):
        print(f"  镜头 {i + 1}: {shot[1]}")
        clips.append(make_clip(i, shot[0], shot[3]))
    print("  交叉转场合成...")
    joined = concat(clips)
    print("  叠加中文字幕...")
    out = add_captions(joined, len(clips))

    size = os.path.getsize(out) / 1024 / 1024
    print()
    print(f"  完成: {out}  ({size:.1f} MB)")
    print("  访问: http://127.0.0.1:8000/static/video/tongren-promo.mp4")


if __name__ == "__main__":
    main()
