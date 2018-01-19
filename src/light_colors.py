import asyncio
import colour
import colorsys
import os
from time import sleep

COLOR_NAMES = [
    'red', 'pink', 'purple', 'blue', 'white', 'yellow', 'green', 'magenta', 'cyan', 'lime'
]

HUES = [ 1, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 359 ] 

def name_2_hsv_color(text):
    named_color = None
    for word in text.split():
        if word in COLOR_NAMES:
            try:
                named_color = colour.Color(word)
            except:
                pass
    if named_color is not None: 
        rgb = list(colorsys.hls_to_rgb(
            named_color.get_hue(), named_color.get_luminance(), named_color.get_saturation()))
        hsv = colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])
        return hsv
    else:
        return False

def color_rotator(bulbs):
    fade_milliseconds = 7000
    for hue in HUES:
        for bulb in bulbs:
            state = bulb.get_light_state()
            state['hue'] = hue
            state['transition_period'] = fade_milliseconds
            bulb.set_light_state(state)
    sleep(fade_milliseconds/1000)

def light_status_file():
    tmpdir = os.getenv('XDG_RUNTIME_DIR')
    filename = tmpdir + os.sep + 'light_status.txt'
    try:
        light_file = open(tmpfile, 'r+')
    except FileNotFoundError:
        light_file = open(tmpfile, 'w+')
    return lightfile 
        
def set_light_status_text(text):
    light_file = light_status_file()
    light_file.truncate()
    light_file.write(text)
    light_file.close()

def get_light_status_text():
    light_file = light_status_file()
    text = light_file.read()
    light_file.close()
    return text


