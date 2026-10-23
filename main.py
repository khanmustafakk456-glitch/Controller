import os
import re
import difflib
import subprocess
import speech_recognition as sr
import ctypes

from pathlib import Path


DESKTOP = Path(os.path.expandvars(r"%USERPROFILE%\Desktop"))


# Direct Windows locations
SPECIAL_LOCATIONS = {
    "this pc": "shell:MyComputerFolder",
    "my computer": "shell:MyComputerFolder",
    "computer": "shell:MyComputerFolder",

    "c drive": "C:\\",
    "local disk c": "C:\\",
    "drive c": "C:\\",

    "downloads": str(Path.home() / "Downloads"),
    "documents folder": str(Path.home() / "Documents"),

    "control panel": "control.exe",
    "network": "explorer.exe shell:NetworkPlacesFolder",
    "recycle bin": "explorer.exe shell:RecycleBinFolder",

    "wondershare filmora": "filmora",
    "wondershare filmora 12": "filmora",
    "itunes": "itunes",
}


def normalize(text):
    text = text.lower().strip()

    # Remove Windows shortcut extensions
    text = re.sub(r"\.(lnk|url)$", "", text)

    # Convert punctuation (including hyphens) into spaces
    text = re.sub(r"[^\w\s]", " ", text)

    return " ".join(text.split())


def clean_command(text):
    text = normalize(text)

    prefixes = [
        "please open ",
        "can you open ",
        "open the folder ",
        "open folder ",
        "open the file ",
        "open file ",
        "open ",
        "folder kholo ",
        "khol do ",
    ]

    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
            break

    for suffix in [" kholo", " khol do", " open karo"]:
        if text.endswith(suffix):
            text = text[:-len(suffix)].strip()

    return text


def open_path(path):
    try:
        os.startfile(str(path))
        print("Opened:", path)

    except Exception as e:
        print("Could not open:", e)


def get_desktop_items():
    items = []

    try:
        for item in DESKTOP.iterdir():
            items.append(item)

    except Exception as e:
        print("Desktop scan error:", e)

    return items


def connect_wifi():
    wifi_name = "vivo V21e"

    try:
        result = subprocess.run(
            ["netsh", "wlan", "connect", f"name={wifi_name}"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            print(f"Wi-Fi connection request sent for: {wifi_name}")

            if result.stdout.strip():
                print(result.stdout.strip())

        else:
            print("Wi-Fi connection request failed.")

            if result.stdout.strip():
                print(result.stdout.strip())

            if result.stderr.strip():
                print(result.stderr.strip())

    except Exception as e:
        print("Wi-Fi error:", e)


def turn_screen_off():
    """Turn off the monitor without putting the PC to sleep."""

    try:
        ctypes.windll.user32.SendMessageW(
            0xFFFF,     # HWND_BROADCAST
            0x0112,     # WM_SYSCOMMAND
            0xF170,     # SC_MONITORPOWER
            2           # Turn monitor off
        )

    except Exception as e:
        print("Screen off error:", e)


def open_item(query):
    query = normalize(query)

    # 1. Wi-Fi voice commands
    wifi_commands = {
        "connect wifi",
        "connect to wifi",
        "wi fi connect",
        "wi fi connect karo",
        "wi fi se connect karo",
        "wifi connect",
        "wifi connect karo",
        "wifi se connect karo",
        "connect wifi karo",
        "vivo v21e",
        "vivo v21e connect",
        "vivo v21e connect karo",
    }

    if query in wifi_commands:
        connect_wifi()
        return

    # 2. Screen Off voice commands
    screen_off_commands = {
        "screen off",
        "turn screen off",
        "screen band karo",
        "display off",
        "display band karo",
        "monitor off",
        "monitor band karo",
    }

    if query in screen_off_commands:
        print("Turning screen off...")
        turn_screen_off()
        return

    # 3. Handle Windows special locations
    if query in SPECIAL_LOCATIONS:
        target = SPECIAL_LOCATIONS[query]

        try:
            if target == "control.exe":
                subprocess.Popen(["control.exe"])

            elif target == "explorer.exe shell:NetworkPlacesFolder":
                subprocess.Popen([
                    "explorer.exe",
                    "shell:NetworkPlacesFolder"
                ])

            elif target == "explorer.exe shell:RecycleBinFolder":
                subprocess.Popen([
                    "explorer.exe",
                    "shell:RecycleBinFolder"
                ])

            elif target in ("filmora", "itunes"):
                import winreg

                app_name = (
                    "Wondershare Filmora"
                    if target == "filmora"
                    else "iTunes"
                )

                roots = [
                    (
                        winreg.HKEY_LOCAL_MACHINE,
                        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
                    ),
                    (
                        winreg.HKEY_LOCAL_MACHINE,
                        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
                    ),
                    (
                        winreg.HKEY_CURRENT_USER,
                        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
                    ),
                ]

                found_path = None

                for root, key_path in roots:
                    try:
                        parent = winreg.OpenKey(root, key_path)

                        for i in range(winreg.QueryInfoKey(parent)[0]):
                            try:
                                sub_name = winreg.EnumKey(parent, i)
                                sub = winreg.OpenKey(parent, sub_name)

                                try:
                                    display, _ = winreg.QueryValueEx(
                                        sub,
                                        "DisplayName"
                                    )

                                except OSError:
                                    sub.Close()
                                    continue

                                if app_name.lower() in display.lower():
                                    try:
                                        found_path, _ = winreg.QueryValueEx(
                                            sub,
                                            "InstallLocation"
                                        )

                                    except OSError:
                                        found_path = None

                                    if found_path and os.path.isdir(found_path):
                                        for file in os.listdir(found_path):
                                            if not file.lower().endswith(".exe"):
                                                continue

                                            if (
                                                "filmora" in file.lower()
                                                if target == "filmora"
                                                else "itunes" in file.lower()
                                            ):
                                                exe_path = os.path.join(
                                                    found_path,
                                                    file
                                                )

                                                subprocess.Popen([exe_path])
                                                found_path = "OPENED"
                                                break

                                sub.Close()

                                if found_path == "OPENED":
                                    break

                            except OSError:
                                continue

                        parent.Close()

                    except OSError:
                        continue

                    if found_path == "OPENED":
                        break

                if found_path != "OPENED":
                    print(
                        f"{app_name} ka launch path nahi mila. "
                        "Start Menu se app search karke batana."
                    )

            elif target.startswith("shell:"):
                subprocess.Popen(["explorer.exe", target])

            else:
                open_path(target)

        except Exception as e:
            print(f"Could not open {query}: {e}")

        return

    # 4. Search Desktop items
    items = get_desktop_items()

    # 5. Exact matching
    exact = [
        item for item in items
        if normalize(item.name) == query
        or normalize(item.stem) == query
    ]

    # 6. Partial matching
    matches = exact or [
        item for item in items
        if query in normalize(item.name)
        or query in normalize(item.stem)
    ]

    # 7. Fuzzy matching
    if not matches:
        names = {
            normalize(item.name): item for item in items
        }

        names.update({
            normalize(item.stem): item for item in items
        })

        close = difflib.get_close_matches(
            query,
            list(names.keys()),
            n=5,
            cutoff=0.55
        )

        matches = [names[name] for name in close]

    # 8. Search one level inside Desktop folders
    if not matches:
        for folder in items:
            if folder.is_dir():
                try:
                    for item in folder.iterdir():
                        if (
                            query in normalize(item.name)
                            or query in normalize(item.stem)
                        ):
                            matches.append(item)

                except (PermissionError, OSError):
                    continue

    if not matches:
        print(f"No matching Desktop item found for: {query}")
        return

    # Remove duplicate paths
    unique = list({
        str(p).lower(): p
        for p in matches
    }.values())

    if len(unique) == 1:
        open_path(unique[0])
        return

    print("\nPossible matches:")

    for i, item in enumerate(unique[:10], 1):
        print(f"{i}. {item.name}")

    choice = input(
        "Enter item number (or press Enter to cancel): "
    ).strip()

    if choice.isdigit() and 1 <= int(choice) <= min(10, len(unique)):
        open_path(unique[int(choice) - 1])

    else:
        print("Cancelled. Please use a more specific name.")


def listen():
    recognizer = sr.Recognizer()

    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8

    try:
        with sr.Microphone() as source:
            print("\nSpeak now...")

            audio = recognizer.listen(
                source,
                timeout=8,
                phrase_time_limit=6
            )

        # Try English first, then Urdu recognition
        try:
            text = recognizer.recognize_google(
                audio,
                language="en-US"
            )

        except sr.UnknownValueError:
            text = recognizer.recognize_google(
                audio,
                language="ur-PK"
            )

        print("Recognized:", text)

        return text

    except sr.WaitTimeoutError:
        print("No speech detected.")

    except sr.UnknownValueError:
        print("Could not understand. Try saying the item name slowly.")

    except sr.RequestError as e:
        print("Speech recognition service error:", e)

    except Exception as e:
        print("Audio error:", e)

    return ""


def main():
    print("CONTROLLER — DESKTOP VOICE ASSISTANT")
    print("Try: Open Controller | Open This PC | Open C Drive")
    print("Try: Connect Wi-Fi | Wi-Fi Connect Karo")
    print("Try: Screen Off | Screen Band Karo")
    print("Say Exit to stop.")

    while True:
        spoken = listen()

        if not spoken:
            continue

        command = normalize(spoken)

        if command in {"exit", "quit", "stop controller"}:
            break

        query = clean_command(spoken)
        open_item(query)


if __name__ == "__main__":
    main()