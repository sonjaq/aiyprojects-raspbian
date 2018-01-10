def roku():
    return ["roku", "row coo", "roku tv"]

def xbox():
    return ["games", "game", "xbox", "video games", "shoot", "blow up", "race", "racing", "netflix"]

def apple_tv():
    return ["apple", "apple tv", "listen", "music", "tunes", "make out", "making out", "airplay"]

def blu_ray():
    return ["blu-ray", "blue ray", "blu ray"]

def nintendo():
    return ["nintendo switch", "nintendo"]

def bluetooth():
    return ["bluetooth", "blue teeth", "blue to", "blue two", "blooptooth"]

def cable():
    return ["cable", "cable sat", "satellite"]

def volume():
    return ["loudness", "quietness", "volume", "quiet", "load", "loud", "up", "down", "mute", "normal"]

def audio_mode():
    return ["dolby", "digital", "surround", "dts", "dps", "mode", "music", "movie", "game", "games", "atmos", "at mo", "neural x", "normal x"]

def receiver_power():
    return ["receiver on", "receiver off", "receiver app", "denon off", "denon app"]

def receiver_name():
    return ["receiver", "denon", "radio", "sound box", "music lady", "dan"]

def receiver_recognition():
    return xbox() + roku() + receiver_name() + apple_tv() + blu_ray() + bluetooth() + nintendo() + audio_mode() + cable()
