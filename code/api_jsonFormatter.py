import random
import time
import requests
import json
import datetime


prefix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def modify_source(source, key_path, value, operation="add"):
    """
    Modify a nested dictionary (source) dynamically.

    Parameters:
    - source (dict): The original dictionary to modify.
    - key_path (list): A list of keys to navigate to the desired location.
    - value: The value to add or update.
    - operation (str): "add" to add or update a value, "remove" to delete a key.

    Returns:
    - dict: The updated dictionary.
    """
    current = source
    for key in key_path[:-1]:  # Navigate to the second-to-last key
        if key not in current:
            current[key] = {}
        current = current[key]

    if operation == "add":
        current[key_path[-1]] = value
    elif operation == "remove":
        current.pop(key_path[-1], None)
    else:
        raise ValueError(f"Unsupported operation: {operation}")

    return source


def add_Image(img):
    source, descriptions, total_duration = img.values()

    img = {
        'type': 'composition',
        'track': 1,
        'duration': total_duration,
        'clip': True,
        'animations': [
            {
                'time': 0,
                'duration': total_duration * 0.1,
                'transition': True,
                'type': 'fade'
            }
        ],
        'elements': [
            {
                'type': 'image',
                'track': 1,
                'time': 0,
                'duration': total_duration,
                'dynamic': True,
                'color_overlay': 'rgba(0,0,0,0.25)',
                'animations': [
                    {
                        'time': 0,
                        'duration': total_duration * 0.1,
                        'easing': 'quadratic-out',
                        'type': 'slide',
                        'direction': '180'
                    },
                    {
                        'time': total_duration * 0.1,
                        'duration': total_duration * 0.9,
                        'easing': 'linear',
                        'type': 'scale',
                        'fade': False,
                        'scope': 'element',
                        'end_scale': '130%',
                        'start_scale': '100%'
                    }
                ],
                'source': source
            }
        ]
    }

    for i, d in enumerate(descriptions):
        if i == 0:
            tts_audio = {
                'type': 'composition',
                'track': 2,
                'time': 0,
                'duration': d['duration'],
                'elements': [
                    {
                        'type': 'text',
                        'track': 1,
                        'time': 0,
                        'x': '5%',
                        'width': '90%',
                        'x_anchor': '0%',
                        'y_anchor': '0%',
                        'x_alignment': '50%',
                        'y_alignment': '50%',
                        'fill_color': '#090101',
                        'animations': [
                            {
                                'easing': 'quadratic-out',
                                'type': 'text-typewriter'
                            }
                        ],
                        'text': d['script'],
                        'font_family': 'Noto Sans',
                        'font_size': '7 vmin',
                        'background_color': 'rgba(255,255,255,1)',
                        'background_x_padding': '10%',
                        'background_y_padding': '10%'
                    },
                    {
                        'type': 'audio',
                        'track': 2,
                        'time': 0,
                        'duration': None,
                        'source': d['audio']
                    }
                ]
            }
        else:
            tts_audio = {
                'type': 'composition',
                'track': 2,
                'time': 0,
                'duration': d['duration'],
                'elements': [
                    {
                        'type': 'text',
                        'track': 1,
                        'time': 0,
                        'x': '5%',
                        'width': '90%',
                        'x_anchor': '0%',
                        'y_anchor': '0%',
                        'x_alignment': '50%',
                        'y_alignment': '50%',
                        'fill_color': '#090101',
                        'animations': [
                            {
                                'easing': 'quadratic-out',
                                'type': 'text-typewriter'
                            }
                        ],
                        'text': d['script'],
                        'font_family': 'Noto Sans',
                        'font_size': '7 vmin',
                        'background_color': 'rgba(255,255,255,1)',
                        'background_x_padding': '10%',
                        'background_y_padding': '10%'
                    },
                    {
                        'type': 'audio',
                        'track': 2,
                        'time': 0,
                        'duration': None,
                        'source': d['audio']
                    }
                ]
            }
        img['elements'].append(tts_audio)
    return img


with open("json/test_information_1.json", "r", encoding="utf-8") as file:
    data = json.load(file)

title, images = data[0].values()

source = {
    'output_format': 'mp4',
    'frame_rate': 60,
    'width': 720,
    'height': 1280,

    'elements': [
        {
            'type': 'composition',
            'track': 1,
            'time': 0,
            'duration': 4,
            'fill_color': f"#{random.randint(0, 0xFFFFFF):06x}",
            'clip': True,
            'elements': [
                {
                    'type': 'text',
                    'track': 1,
                    'time': 0,
                    'duration': 3,
                    'dynamic': True,
                    'width': '52.2433%',
                    'height': '35.6373%',
                    'x_alignment': '50%',
                    'y_alignment': '50%',
                    'fill_color': '#ffffff',
                    'animations': [
                        {
                            'time': 'end',
                            'duration': 3,
                            'easing': 'quadratic-out',
                            'type': 'text-typewriter',
                            'typing_start': '0 s',
                            'typing_duration': '1.5 s',
                        },
                        {
                            'time': 'end',
                            'duration': 2.35,
                            'easing': 'linear',
                            'type': 'scale',
                            'fade': False,
                            'scope': 'element',
                            'track': 0,
                            'start_scale': '130%'
                        }
                    ],
                    'text': f"{title}",
                    'font_family': 'Yeon Sung',
                    'font_size_minimum': '10 vmin',
                    'font_size_maximum': '20 vmin',
                    'text_transform': 'uppercase'
                }
            ]
        },
    ]
}

for img in images:
    source['elements'].append(add_Image(img))

with open('json/api_test_1.json', 'w') as json_file:
    json.dump(source, json_file, indent=4)

url = "https://api.creatomate.com/v1/renders"
headers = {
    "Authorization": "Bearer 929260bbc9c24512bde07fe182f08f00243dc3f68c92fc8ec5789fa2a8a1122f636b0c04df95136ce9b29f137602f8f2",
    "Content-Type": "application/json",
}


response = requests.post(url, headers=headers, json={'source': source})
response_data = response.json()
render_id = response_data[0]["id"]
status_url = f"{url}/{render_id}"

while True:
    status_response = requests.get(status_url, headers=headers)
    status_data = status_response.json()

    print(f"Current status: {status_data['status']}")

    if status_data["status"] == "succeeded":
        file_url = status_data["url"]
        print(f"Video completed: {file_url}")
        break
    elif status_data["status"] == "failed":
        raise RuntimeError("Video rendering failed.")

    time.sleep(5)

file_name = prefix + '_' + 'test_1' + file_url.split('/')[-1]
file_response = requests.get(file_url)

with open(file_name, "wb") as file:
    file.write(file_response.content)
print(f"Video saved as {file_name}")
