import datetime
import json
import os
import re
import ffmpeg
from gtts import gTTS
from datetime import timedelta
import subprocess


prefix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def find_nearest_comma(sentence):
    """
    문자열에서 중앙에 가장 가까운 쉼표 위치를 반환하는 함수

    Args:
        sentence (string): 쉼표를 찾을 문장 문자열

    Returns:
        문자열 내 쉼표 위치 인덱스
    """
    comma_positions = [i for i, char in enumerate(sentence) if char == ","]
    if not comma_positions:
        return -1  # 쉼표가 없다면 -1 반환
    mid_pos = len(sentence) // 2
    # 쉼표와 중앙의 차이를 계산하여 가장 가까운 쉼표 선택
    nearest_comma = min(comma_positions, key=lambda x: abs(x - mid_pos))
    return nearest_comma


def get_audio_duration(file_path):
    """
    mp3 오디오 소스의 재생 시간을 반환하는 함수

    Args:
        file_path (path): 소스 경로

    Returns:
        float: 재생 시간
    """
    probe = ffmpeg.probe(
        file_path, v="error", select_streams="a", show_entries="format=duration"
    )
    duration = float(probe["format"]["duration"])
    return duration


def split_sentence(sentence, max_length, comma_splited):
    """
    문장을 max_length 값에 맞춰서 구분하는 함수

    Args:
        script (List): 전체 문장을 포함하는 리스트 (json 파일의 section 키의 값)
        max_length (int): 최대 문장 길이
    Returns:
        List: 분할된 문장 리스트
    """

    # 길이가 max_length 이하라면 그 문장을 그대로 반환
    if len(sentence) <= max_length:
        return [sentence]

    # 해당 문장이 쉼표로 구분 된 문장이 아니라면(쉼표로 구분 된 문장일 시 해당 문장의 맨 끝은 쉼표이며, 이 때문에 오류가 날 수 있다.)
    if comma_splited == 0:
        # 쉼표가 있는지 확인하고, 있으면 쉼표 기준으로 나누기
        comma_pos = find_nearest_comma(sentence)
        if comma_pos != -1:
            first_part = sentence[: comma_pos + 1]
            second_part = sentence[comma_pos + 1:].strip()
            # 첫 번째 부분(comma_splited = 1)과 두 번째 부분에 대해 재귀 호출
            return split_sentence(first_part, max_length, 1) + split_sentence(
                second_part, max_length, 0
            )

    # 쉼표가 없다면, 문장의 중간에서 공백을 기준으로 나누기
    mid_pos = len(sentence) // 2
    left_pos = sentence.rfind(
        " ", 0, mid_pos
    )  # 문장의 시작부터 중간까지 중 가장 마지막 공백 위치
    right_pos = sentence.find(
        " ", mid_pos
    )  # 문장 중간부터 끝까지 중 가장 처음 공백 위치

    # 양쪽 공백 중, 더 적절한 곳에서 나누기
    if left_pos != -1 and (
        right_pos == -1 or mid_pos - left_pos <= right_pos - mid_pos
    ):
        return split_sentence(sentence[:left_pos], max_length, 0) + split_sentence(
            sentence[left_pos + 1:], max_length, 0
        )
    elif right_pos != -1:
        return split_sentence(sentence[:right_pos], max_length, 0) + split_sentence(
            sentence[right_pos + 1:], max_length, 0
        )
    # 더 이상 나눌 수 없으면 그대로 반환
    return [sentence]


def is_valid_tts_string(text):
    # 공백이거나 비어있는 문자열인지 확인
    if not text.strip():
        return False
    # 문자열에 알파벳, 숫자, 또는 공백이 포함되어 있으면 유효한 문자열로 간주
    if any(char.isalnum() for char in text):
        return True
    return False


def section_to_script(script, max_length):
    """
    전체 스크립트를 온점(.)을 기준으로 나누고 여러 문장으로 나누고, 각 문장 길이가 max_length를 초과할 경우 공백이나 쉼표에서 적절히 잘라 알맞은 길이의 자막 리스트를 반환하는 함수

    Args:
        script (List): 전체 문장을 포함하는 리스트 (json 파일의 section 키의 값)
        max_length (int): 최대 문장 길이
    Returns:
        List: 분할된 문장 리스트
    """
    result = []
    # full_text = " ".join(script)
    # 온점(.) 기준으로 문장 나누기
    # sentences = re.split(r"(?<=[.!?])\s*", full_text)
    sentences = re.split(r"(?<=[.!?])\s*", script)
    sentences.pop()

    # 나눈 문장들을 다시 조합해서 문장 리스트로 만듦
    for s in sentences:
        result += split_sentence(s, max_length, 0)
    result = [text for text in result if is_valid_tts_string(text)]
    return result


def add_time_to_timer(timer, seconds_to_add):
    """
    .srt 파일에 작성하기 위한 시간 포맷을 작성하기 위해 영상 재생 길이를 더하여 문자열로 반환하는 함수

    Args:
        timer (string): '00:00:00,000' 형식의 문자열
        seconds_to_add (float): 영상의 재생 길이
    Returns:
        string: 재생 시간만큼 더한 .srt 형식의 시간 포맷 문자열
    """
    # "00:00:00,000" 형식을 분해
    h, m, s_ms = timer.split(":")
    s, ms = map(int, s_ms.split(","))

    # timer 값에 시간 더하기
    added_time = timedelta(
        hours=int(h), minutes=int(m), seconds=int(s), milliseconds=ms
    ) + timedelta(seconds=seconds_to_add)

    # 결과를 "00:00:00,000" 형식으로 변환
    total_seconds = int(added_time.total_seconds())
    milliseconds = int(added_time.microseconds / 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def create_video(image_dir, audio_file, subtitle_file, output_file):
    """
    FFmpeg를 사용하여 이미지, 오디오, 자막을 결합해 동영상을 생성하는 함수.

    Args:
        image_dir (path): 이미지 파일 경로
        audio_file (path): 오디오 파일 경로
        subtitle_file (path): 자막 파일 경로
        output_file (path): 출력 동영상 파일 경로
    """
    # audio_duration = get_audio_duration(audio_file)
    # num_images = len(sorted(
    #         [
    #             os.path.join(image_dir, f)
    #             for f in os.listdir(image_dir)
    #             if f.endswith(".jpg")
    #         ]
    #     ))
    # image_duration = audio_duration / num_images
    # framerate = num_images / audio_duration
    # image_pattern = os.path.join(image_dir, "sample_%d.jpg")

    try:
        # FFmpeg 명령 실행
        subprocess.run(
            [
                "ffmpeg",
                "-f", "concat",
                "-i", image_dir,
                "-f", "concat",
                "-i", audio_file,
                "-vf", f"format=yuv420p,pad=ceil(iw/2)*2:ceil(ih/2)*2,subtitles={
                    subtitle_file}",
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "copy",
                "-b:a", "192k",
                "-shortest",
                "-y",
                output_file,
            ],
            check=True,
        )
        print(f"동영상 생성 완료: {output_file}")
    except subprocess.CalledProcessError as e:
        print("FFmpeg 실행 중 오류가 발생했습니다.", e)
    except FileNotFoundError:
        print("FFmpeg가 설치되어 있지 않거나 PATH에 설정되어 있지 않습니다.")


def script_to_TTS(scripts, image_number, category_number):
    audios = []
    durations = []
    total_duration = 0
    for i, s in enumerate(scripts):
        audio_path = f"audio/{prefix}_category_{category_number}_img_{image_number}_audio_{i}.mp3"
        gTTS(text=s, lang='ko').save(audio_path)
        audios.append(audio_path)
        duration = get_audio_duration(audio_path)
        total_duration += duration
        durations.append(duration)
    return audios, durations, total_duration


# JSON 파일에서 데이터 읽기
with open("json/result.json", "r", encoding="utf-8") as file:
    data = json.load(file)

max_length = 20  # 최대 길이 설정

information = []
for i, d in enumerate(data):
    category, title, section, image = d.values()

    images = []
    for j, img in enumerate(image):
        source = img[0]
        script = section[j]
        scripts = section_to_script(script, max_length)
        print(scripts)

        tts, durations, total_duration = script_to_TTS(scripts, j, i)

        descriptions = []
        for k, s in enumerate(scripts):
            descriptions.append({'script': scripts[k],
                                 'audio': tts[k],
                                 'duration': durations[k]})

        images.append({'source': source,
                       'descriptions': descriptions,
                       'total_duration': total_duration})
    information.append({'title': title,
                        'images': images})

with open('json/test_information_1.json', 'w') as json_file:
    json.dump(information, json_file, indent=4)  # indent=4는 들여쓰기를 4칸으로 설정


"""
       summary = {
       'title': title,
       'images': [
           {
               'source': data[0]["image"][0][0],
               'descriptions': [
                   {
                       'script': scripts,
                       'audio': tts,
                       'duration': duration
                   },
                   {
                       'scripts': scripts,
                       'audio': tts,
                       'duration': duration
                   },
                   {
                       'scripts': scripts,
                       'audio': tts,
                       'duration': duration
                   }
               ],
               'total_duration': total_duration
           },
           {
               'source': data[0]["image"][0][0],
               'descriptions': [
                   {
                       'scripts': scripts,
                       'audio': tts,
                       'duration': duration
                   },
                   {
                       'scripts': scripts,
                       'audio': tts,
                       'duration': duration
                   },
                   {
                       'scripts': scripts,
                       'audio': tts,
                       'duration': duration
                   }
               ]
           },
           {
               'source': data[0]["image"][0][0],
               'descriptions': [
                   {
                       'scripts': scripts,
                       'audio': tts,
                       'duration': duration
                   },
                   {
                       'scripts': scripts,
                       'audio': tts,
                       'duration': duration
                   },
                   {
                       'scripts': scripts,
                       'audio': tts,
                       'duration': duration
                   }
               ]
           }
       ]
   }"""
