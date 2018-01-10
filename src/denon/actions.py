"""
List of commands valid for the Denon AVR-X1400H receiver that I want to use
"""
def receiver_power_on():
    return b"ZMON\r"

def receiver_standby():
    return b"ZMOFF\r"

def roku_tv():
    return b"SITV\r"

def xbox():
    return b"SIGAME\r"

def apple_tv():
    return b"SIMPLAY\r"

def bluetooth():
    return b"SIBT\r"

def nintendo():
    return b"SIDVD\r"

def blu_ray():
    return b"SIBD\r"

def cable():
    return b"SISAT/CABLE\r"

def volume_up():
    return b"MVUP\r" * 10

def volume_down():
    return b"MVDOWN\r"

def volume_quiet():
    return b"MV20\r"

def volume_loud():
    return b"MV60\r"

def volume_normal():
    return b"MV42\r"

def volume_mute():
    return b"MUON\r"

def volume_unmute():
    return b"MUOFF\r"

def xbox_game():
    return b"SIGAME\rMSGAME\r"

def xbox_movie():
    return b"SIGAME\rMSMOVIE\r"

def xbox_movie_stereo():
    return b"SIGAME\rMSSTEREO\r"

def apple_tv_music():
    return b"SIMPLAY\rMSMUSIC\r"

def apple_tv_movie():
    return b"SIMPLAY\rMSMOVIE\r"

def apple_tv_stereo():
    return b"SIMPLAY\rMSSTEREO\r"

def bluetooth_music():
    return b"SIBT\rMSMUSIC\r"

def bluetooth_movie():
    return b"SIBT\rMSMOVIE\r"

def bluetooth_stereo():
    return b"SIBT\rMSSTEREO\r"


def mode_music():
    return b"MSMUSIC\r"

def mode_movie():
    return b"MSMOVIE\r"

def mode_stereo():
    return b"MSSTEREO\r"
