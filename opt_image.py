import os
import subprocess
import sys
from PIL import Image, ImageFile

# Pillow가 일부 손상된 이미지를 처리하도록 허용
ImageFile.LOAD_TRUNCATED_IMAGES = True

def optimize_images(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(".jpg") or file.lower().endswith(".jpeg"):
                optimize_jpg(file_path)
            elif file.lower().endswith(".png"):
                optimize_png(file_path)

def optimize_jpg(file_path):
    try:
        # 원본 파일 크기
        original_size = os.path.getsize(file_path)

        # 이미지 열기
        with Image.open(file_path) as img:
            # EXIF 데이터 제거
            img_without_exif = Image.new(img.mode, img.size)
            img_without_exif.putdata(list(img.getdata()))
            
            # 임시 저장 경로
            temp_path = file_path + ".temp"
            
            # 이미지 최적화 및 저장
            img_without_exif.save(temp_path, "JPEG", quality=90, optimize=True)
        
        # 최적화된 파일 크기
        optimized_size = os.path.getsize(temp_path)

        # 크기 비교 및 결과 처리
        if optimized_size < original_size:
            print_compression_stats(file_path, original_size, optimized_size)
            os.replace(temp_path, file_path)  # 최적화된 파일 덮어쓰기
        else:
            print(f"Skipped {file_path}: Optimized file is larger or same size.")
            os.remove(temp_path)  # 임시 파일 삭제
    except Exception as e:
        print(f"Failed to optimize JPG {file_path}: {e}")

def optimize_png(file_path):
    try:
        # 원본 파일 크기
        original_size = os.path.getsize(file_path)

        # `pngquant` 실행 경로 및 명령어 구성
        temp_path = file_path + ".temp"
        pngquant_command = [
            "pngquant", "--force", "--output", temp_path, "--quality=60-90", file_path
        ]

        # `pngquant` 실행
        subprocess.run(pngquant_command, check=True)

        # 최적화된 파일 크기
        optimized_size = os.path.getsize(temp_path)

        # 크기 비교 및 결과 처리
        if optimized_size < original_size:
            print_compression_stats(file_path, original_size, optimized_size)
            os.replace(temp_path, file_path)  # 최적화된 파일 덮어쓰기
        else:
            print(f"Skipped {file_path}: Optimized file is larger or same size.")
            os.remove(temp_path)  # 임시 파일 삭제
    except subprocess.CalledProcessError as e:
        print(f"Failed to optimize PNG {file_path}: pngquant error - {e}")
    except Exception as e:
        print(f"Failed to optimize PNG {file_path}: {e}")

def print_compression_stats(file_path, original_size, optimized_size):
    size_diff = original_size - optimized_size
    percentage = abs(size_diff) / original_size * 100

    print(f"Reduced size for {file_path}: {size_diff / 1024:.2f} KB ({percentage:.2f}% smaller).")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python optimize_images.py <directory>")
        sys.exit(1)

    target_directory = sys.argv[1]
    if os.path.isdir(target_directory):
        print(f"Starting image optimization in: {target_directory}")
        optimize_images(target_directory)
        print("Image optimization complete.")
    else:
        print(f"Invalid directory path: {target_directory}")
        sys.exit(1)
