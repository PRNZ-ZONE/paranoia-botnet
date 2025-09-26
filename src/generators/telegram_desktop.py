import random


# TAKEN FROM OPENTELE & https://github.com/json1c/telegram-raid-botnet/blob/master/modules/generators/linux.py
# TY BLOODY
class Application:
    lang_pack: str = "tdesktop"

    enviroments = [
        "GNOME",
        "MATE",
        "XFCE",
        "Cinnamon",
        "Unity",
        "ubuntu",
        "LXDE",
        "i3",
        "Openbox",
        "bspwm",
        "dwm",
        "KDE",
    ]
    compositors = ["Wayland", "XWayland", "X11"]
    glibc_versions = ["2.32", "2.33", "2.34", "2.35"]
    app_versions = ["4.0.2 x64", "4.0.2", "3.7.3 x64", "3.6.1", "3.1.1 x64", "3.1.1"]

    @staticmethod
    def system_lang_code() -> str:
        return random.choice(["zh-hans", "cn", "en", "ru", "af", "sq", "cs", "pl"])

    @staticmethod
    def app_version() -> str:
        return random.choice(Application.app_versions)

    @staticmethod
    def device() -> str:
        return "PC 64bit"

    @staticmethod
    def sdk() -> str:
        enviroment = random.choice(Application.enviroments)
        compositor = random.choice(Application.compositors)
        glibc_version = random.choice(Application.glibc_versions)
        return f"Linux {enviroment} {compositor} glibc {glibc_version}"
