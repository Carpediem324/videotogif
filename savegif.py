#!/usr/bin/env python3
import subprocess
import sys
import os

# —————————— 최적화 및 해상도 축소 파라미터 설정 ——————————
# GIF 저장 시 사용될 옵션입니다.
# ImageMagick 대신 ffmpeg로 처리하도록 수정
OPTIMIZE = {
    'fps': 10,                     # 출력 GIF의 초당 프레임 수
    'program': 'ffmpeg',           # ffmpeg 엔진 사용
    'opt': None,                   # ImageMagick 전용 옵션 비활성화
    'verbose': False,
    'logger': None
}
# 해상도 축소 비율 (예: 0.5 → 가로/세로 절반 크기)
RESIZE_RATIO = 0.5
# ————————————————————————————————————————————————

# 저장 포맷 선택: 'gif' 또는 'webp'
SAVE_FORMAT = "gif"  # 'gif' 또는 'webp'로 변경 가능

# 현재 파이썬 파일의 위치 기준으로 동영상 파일과 저장 위치 지정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(SCRIPT_DIR, 'fastvideo')

### 수정할 곳
VIDEO_PATH = os.path.join(SCRIPT_DIR, 'c202_0519.mp4')
OUTPUT_FILENAME = 'c202-2'             # 저장할 파일명 (확장자 제외)
SPEED_FACTOR = 2.0                     # 몇 배속 (예: 2.0이면 2배속)
# ————————————————————————————————————————————————

# setuptools(및 pkg_resources) 임포트 (설치되어 있지 않으면 설치)
try:
    import pkg_resources
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "setuptools"], check=True)
    import pkg_resources

from pkg_resources import parse_version

def version_satisfies(installed_version, constraint):
    if constraint.startswith("=="):
        required_version = constraint[2:]
        return parse_version(installed_version) == parse_version(required_version)
    elif constraint.startswith(">="):
        required_version = constraint[2:]
        return parse_version(installed_version) >= parse_version(required_version)
    else:
        return True

def check_and_install_packages():
    required_packages = [
        ("moviepy", "==1.0.3"),
        ("imageio", ">=2.5.0"),
        ("decorator", ">=4.3.0"),
        ("tqdm", ">=4.0.0"),
        ("Pillow", ">=7.0.0"),
        ("scipy", ">=1.3.0"),
        ("pydub", ">=0.23.0"),
        ("audiofile", ">=0.0.0"),
        ("opencv-python", ">=4.5"),
        ("numpy", "==1.24.3")
    ]
    for pkg, constraint in required_packages:
        try:
            installed_version = pkg_resources.get_distribution(pkg).version
            if version_satisfies(installed_version, constraint):
                print(f"{pkg} {installed_version} (요구: {constraint}) - 만족함")
                continue
            else:
                print(f"{pkg} {installed_version} (요구: {constraint}) - 버전 불일치")
        except pkg_resources.DistributionNotFound:
            print(f"{pkg}이(가) 설치되어 있지 않습니다. (요구: {constraint})")
        install_cmd = [sys.executable, "-m", "pip", "install"]
        if pkg == "numpy":
            install_cmd += ["--upgrade", "--force-reinstall", f"{pkg}{constraint}"]
        else:
            install_cmd += [f"{pkg}{constraint}"]
        print("실행 명령어:", " ".join(install_cmd))
        subprocess.run(install_cmd, check=True)

check_and_install_packages()

try:
    from moviepy.editor import VideoFileClip, vfx
except ImportError:
    raise ImportError("moviepy 모듈을 불러올 수 없습니다. 패키지 설치를 확인하세요.")

def write_webp(clip, output_file):
    from PIL import Image
    frames = [Image.fromarray(frame) for frame in clip.iter_frames()]
    fps = int(round(clip.fps))
    duration = int(round(1000 / fps))
    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        format='WEBP'
    )

def change_video_speed():
    os.makedirs(SAVE_PATH, exist_ok=True)
    if SAVE_FORMAT.lower() == "gif":
        output_file = os.path.join(SAVE_PATH, OUTPUT_FILENAME + '.gif')
    elif SAVE_FORMAT.lower() == "webp":
        output_file = os.path.join(SAVE_PATH, OUTPUT_FILENAME + '.webp')
    else:
        raise ValueError("SAVE_FORMAT 설정이 잘못되었습니다.")

    print(f"원본 파일: {VIDEO_PATH}")
    print(f"저장 파일: {output_file}")
    print(f"속도 변경 배수: {SPEED_FACTOR}")
    print(f"해상도 축소 비율: {RESIZE_RATIO * 100:.0f}%")

    clip = VideoFileClip(VIDEO_PATH)
    sped_up_clip = clip.fx(vfx.speedx, factor=SPEED_FACTOR).resize(RESIZE_RATIO)

    if SAVE_FORMAT.lower() == "gif":
        kwargs = {k: v for k, v in OPTIMIZE.items() if v is not None}
        sped_up_clip.write_gif(output_file, **kwargs)
    else:
        write_webp(sped_up_clip, output_file)

    clip.close()
    sped_up_clip.close()
    print("변환 완료!")

if __name__ == "__main__":
    change_video_speed()
