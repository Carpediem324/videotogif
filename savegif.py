#!/usr/bin/env python3
import subprocess
import sys
import os

# 전역변수 설정 (필요에 따라 아래 값을 수정하세요)
# 저장 포맷 선택: 'gif' 또는 'webp'
SAVE_FORMAT = "webp"  # 'gif' 또는 'webp'로 변경 가능

# 현재 파이썬 파일의 위치를 기준으로 동영상 파일과 저장 위치를 지정합니다.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(SCRIPT_DIR, 'fastvideo')

### 수정할곳
VIDEO_PATH = os.path.join(SCRIPT_DIR, 'dsss.mp4')
OUTPUT_FILENAME = 'dsss'             # 저장할 파일명 (확장자 제외)
SPEED_FACTOR = 5.0                       # 몇 배속 (예: 2.0이면 2배속)

# setuptools(및 pkg_resources) 임포트 (설치되어 있지 않으면 설치)
try:
    import pkg_resources
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "setuptools"], check=True)
    import pkg_resources

from pkg_resources import parse_version

def version_satisfies(installed_version, constraint):
    """
    단순하게 '=='와 '>=' 조건만 처리합니다.
    """
    if constraint.startswith("=="):
        required_version = constraint[2:]
        return parse_version(installed_version) == parse_version(required_version)
    elif constraint.startswith(">="):
        required_version = constraint[2:]
        return parse_version(installed_version) >= parse_version(required_version)
    else:
        # 다른 조건은 무시하고 True로 간주합니다.
        return True

def check_and_install_packages():
    # 설치할 패키지 목록 (패키지명, 버전조건)
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
        
        # numpy는 강제 재설치 옵션 적용
        if pkg == "numpy":
            install_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", f"{pkg}{constraint}"]
        else:
            install_cmd = [sys.executable, "-m", "pip", "install", f"{pkg}{constraint}"]
        print("실행 명령어:", " ".join(install_cmd))
        subprocess.run(install_cmd, check=True)

# 필요한 패키지들을 확인하고 설치합니다.
check_and_install_packages()

# 설치한 패키지들을 import 합니다.
try:
    from moviepy.editor import VideoFileClip, vfx
except ImportError:
    raise ImportError("moviepy 모듈을 불러올 수 없습니다. 패키지 설치를 확인하세요.")

def write_webp(clip, output_file):
    """
    VideoClip 객체를 받아서 animated webp 파일로 저장합니다.
    Pillow의 Image.save()를 사용하여 save_all 옵션으로 저장합니다.
    """
    from PIL import Image
    frames = []
    # 모든 프레임을 리스트에 저장합니다.
    for frame in clip.iter_frames():
        im = Image.fromarray(frame)
        frames.append(im)
    
    # fps를 정수로 변환하고, 프레임 간 간격(duration)을 밀리초 단위로 계산합니다.
    fps = int(round(clip.fps))
    duration = int(round(1000 / fps))
    
    # 첫 번째 프레임에 나머지 프레임을 추가하여 animated webp 파일로 저장합니다.
    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        format='WEBP'
    )

def change_video_speed():
    # 저장 경로가 없으면 생성합니다.
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    
    # SAVE_FORMAT 값에 따라 확장자를 붙입니다.
    if SAVE_FORMAT.lower() == "gif":
        output_file = os.path.join(SAVE_PATH, OUTPUT_FILENAME + '.gif')
    elif SAVE_FORMAT.lower() == "webp":
        output_file = os.path.join(SAVE_PATH, OUTPUT_FILENAME + '.webp')
    else:
        raise ValueError("SAVE_FORMAT 설정이 잘못되었습니다. 'gif' 또는 'webp'로 설정해주세요.")
    
    print(f"원본 파일: {VIDEO_PATH}")
    print(f"저장 파일: {output_file}")
    print(f"속도 변경 배수: {SPEED_FACTOR}")
    
    # 비디오 파일 불러오기
    clip = VideoFileClip(VIDEO_PATH)
    
    # 속도 변경 (moviepy의 vfx.speedx 함수 사용)
    sped_up_clip = clip.fx(vfx.speedx, factor=SPEED_FACTOR)
    
    # SAVE_FORMAT 값에 따라 gif 또는 webp로 저장
    if SAVE_FORMAT.lower() == "gif":
        sped_up_clip.write_gif(output_file)
    elif SAVE_FORMAT.lower() == "webp":
        write_webp(sped_up_clip, output_file)
    
    # 클립 리소스 해제
    clip.close()
    sped_up_clip.close()

if __name__ == "__main__":
    change_video_speed()
