# Copyright 2021 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import re
import subprocess
import itertools
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set

RESULT = (Path(__file__) / "../../aosp.json").resolve()
DOWNLOADS = (Path(__file__) / "../../../../downloads").resolve()

# List below generated by running the following snippet in the DevTools console
# on the following page:
# https://android.googlesource.com/
# console.log(Array.from(document.querySelectorAll(
#   "a.RepoList-item[href*='/platform/packages/apps/']"
# )).map(a=>`    (
#         "${a.href.split('/').reverse()[1]}",
#         "${a.href}",
#     ),`).join('\n'))
APP_GIT_REPOS = [
    (
        "AccountsAndSyncSettings",
        "https://android.googlesource.com/platform/packages/apps/AccountsAndSyncSettings/",  # noqa: E501
    ),
    (
        "AlarmClock",
        "https://android.googlesource.com/platform/packages/apps/AlarmClock/",
    ),
    (
        "BasicSmsReceiver",
        "https://android.googlesource.com/platform/packages/apps/BasicSmsReceiver/",
    ),
    (
        "Benchmark",
        "https://android.googlesource.com/platform/packages/apps/Benchmark/",
    ),
    (
        "Bluetooth",
        "https://android.googlesource.com/platform/packages/apps/Bluetooth/",
    ),
    (
        "Browser",
        "https://android.googlesource.com/platform/packages/apps/Browser/",
    ),
    (
        "Browser2",
        "https://android.googlesource.com/platform/packages/apps/Browser2/",
    ),
    (
        "Calculator",
        "https://android.googlesource.com/platform/packages/apps/Calculator/",
    ),
    (
        "Calendar",
        "https://android.googlesource.com/platform/packages/apps/Calendar/",
    ),
    (
        "Camera",
        "https://android.googlesource.com/platform/packages/apps/Camera/",
    ),
    (
        "Camera2",
        "https://android.googlesource.com/platform/packages/apps/Camera2/",
    ),
    (
        "Calendar",
        "https://android.googlesource.com/platform/packages/apps/Car/Calendar/",
    ),
    (
        "Cluster",
        "https://android.googlesource.com/platform/packages/apps/Car/Cluster/",
    ),
    (
        "CompanionDeviceSupport",
        "https://android.googlesource.com/platform/packages/apps/Car/CompanionDeviceSupport/",  # noqa: E501
    ),
    (
        "Dialer",
        "https://android.googlesource.com/platform/packages/apps/Car/Dialer/",
    ),
    (
        "externallibs",
        "https://android.googlesource.com/platform/packages/apps/Car/externallibs/",
    ),
    (
        "Hvac",
        "https://android.googlesource.com/platform/packages/apps/Car/Hvac/",
    ),
    (
        "LatinIME",
        "https://android.googlesource.com/platform/packages/apps/Car/LatinIME/",
    ),
    (
        "Launcher",
        "https://android.googlesource.com/platform/packages/apps/Car/Launcher/",
    ),
    (
        "LensPicker",
        "https://android.googlesource.com/platform/packages/apps/Car/LensPicker/",
    ),
    (
        "libs",
        "https://android.googlesource.com/platform/packages/apps/Car/libs/",
    ),
    (
        "LinkViewer",
        "https://android.googlesource.com/platform/packages/apps/Car/LinkViewer/",
    ),
    (
        "LocalMediaPlayer",
        "https://android.googlesource.com/platform/packages/apps/Car/LocalMediaPlayer/",
    ),
    (
        "Media",
        "https://android.googlesource.com/platform/packages/apps/Car/Media/",
    ),
    (
        "Messenger",
        "https://android.googlesource.com/platform/packages/apps/Car/Messenger/",
    ),
    (
        "Notification",
        "https://android.googlesource.com/platform/packages/apps/Car/Notification/",
    ),
    (
        "Overview",
        "https://android.googlesource.com/platform/packages/apps/Car/Overview/",
    ),
    (
        "Provision",
        "https://android.googlesource.com/platform/packages/apps/Car/Provision/",
    ),
    (
        "Radio",
        "https://android.googlesource.com/platform/packages/apps/Car/Radio/",
    ),
    (
        "RotaryController",
        "https://android.googlesource.com/platform/packages/apps/Car/RotaryController/",
    ),
    (
        "Settings",
        "https://android.googlesource.com/platform/packages/apps/Car/Settings/",
    ),
    (
        "Stream",
        "https://android.googlesource.com/platform/packages/apps/Car/Stream/",
    ),
    (
        "SystemUpdater",
        "https://android.googlesource.com/platform/packages/apps/Car/SystemUpdater/",
    ),
    (
        "Templates",
        "https://android.googlesource.com/platform/packages/apps/Car/Templates/",
    ),
    (
        "tests",
        "https://android.googlesource.com/platform/packages/apps/Car/tests/",
    ),
    (
        "UserManagement",
        "https://android.googlesource.com/platform/packages/apps/Car/UserManagement/",
    ),
    (
        "CarrierConfig",
        "https://android.googlesource.com/platform/packages/apps/CarrierConfig/",
    ),
    (
        "CellBroadcastReceiver",
        "https://android.googlesource.com/platform/packages/apps/CellBroadcastReceiver/",
    ),
    (
        "CertInstaller",
        "https://android.googlesource.com/platform/packages/apps/CertInstaller/",
    ),
    (
        "Contacts",
        "https://android.googlesource.com/platform/packages/apps/Contacts/",
    ),
    (
        "ContactsCommon",
        "https://android.googlesource.com/platform/packages/apps/ContactsCommon/",
    ),
    (
        "DeskClock",
        "https://android.googlesource.com/platform/packages/apps/DeskClock/",
    ),
    (
        "DevCamera",
        "https://android.googlesource.com/platform/packages/apps/DevCamera/",
    ),
    (
        "Dialer",
        "https://android.googlesource.com/platform/packages/apps/Dialer/",
    ),
    (
        "DocumentsUI",
        "https://android.googlesource.com/platform/packages/apps/DocumentsUI/",
    ),
    (
        "Email",
        "https://android.googlesource.com/platform/packages/apps/Email/",
    ),
    (
        "EmergencyInfo",
        "https://android.googlesource.com/platform/packages/apps/EmergencyInfo/",
    ),
    (
        "ExactCalculator",
        "https://android.googlesource.com/platform/packages/apps/ExactCalculator/",
    ),
    (
        "Exchange",
        "https://android.googlesource.com/platform/packages/apps/Exchange/",
    ),
    (
        "FMRadio",
        "https://android.googlesource.com/platform/packages/apps/FMRadio/",
    ),
    (
        "Gallery",
        "https://android.googlesource.com/platform/packages/apps/Gallery/",
    ),
    (
        "Gallery2",
        "https://android.googlesource.com/platform/packages/apps/Gallery2/",
    ),
    (
        "Gallery3D",
        "https://android.googlesource.com/platform/packages/apps/Gallery3D/",
    ),
    (
        "GlobalSearch",
        "https://android.googlesource.com/platform/packages/apps/GlobalSearch/",
    ),
    (
        "GoogleSearch",
        "https://android.googlesource.com/platform/packages/apps/GoogleSearch/",
    ),
    (
        "HTMLViewer",
        "https://android.googlesource.com/platform/packages/apps/HTMLViewer/",
    ),
    (
        "IdentityCredentialSupport",
        "https://android.googlesource.com/platform/packages/apps/IdentityCredentialSupport/",  # noqa: E501
    ),
    (
        "IM",
        "https://android.googlesource.com/platform/packages/apps/IM/",
    ),
    (
        "ImsServiceEntitlement",
        "https://android.googlesource.com/platform/packages/apps/ImsServiceEntitlement/",
    ),
    (
        "InCallUI",
        "https://android.googlesource.com/platform/packages/apps/InCallUI/",
    ),
    (
        "KeyChain",
        "https://android.googlesource.com/platform/packages/apps/KeyChain/",
    ),
    (
        "Launcher",
        "https://android.googlesource.com/platform/packages/apps/Launcher/",
    ),
    (
        "Launcher2",
        "https://android.googlesource.com/platform/packages/apps/Launcher2/",
    ),
    (
        "Launcher3",
        "https://android.googlesource.com/platform/packages/apps/Launcher3/",
    ),
    (
        "LegacyCamera",
        "https://android.googlesource.com/platform/packages/apps/LegacyCamera/",
    ),
    (
        "ManagedProvisioning",
        "https://android.googlesource.com/platform/packages/apps/ManagedProvisioning/",
    ),
    (
        "McLauncher",
        "https://android.googlesource.com/platform/packages/apps/McLauncher/",
    ),
    (
        "Messaging",
        "https://android.googlesource.com/platform/packages/apps/Messaging/",
    ),
    (
        "Mms",
        "https://android.googlesource.com/platform/packages/apps/Mms/",
    ),
    (
        "Music",
        "https://android.googlesource.com/platform/packages/apps/Music/",
    ),
    (
        "MusicFX",
        "https://android.googlesource.com/platform/packages/apps/MusicFX/",
    ),
    (
        "Nfc",
        "https://android.googlesource.com/platform/packages/apps/Nfc/",
    ),
    (
        "OnDeviceAppPrediction",
        "https://android.googlesource.com/platform/packages/apps/OnDeviceAppPrediction/",
    ),
    (
        "OneTimeInitializer",
        "https://android.googlesource.com/platform/packages/apps/OneTimeInitializer/",
    ),
    (
        "PackageInstaller",
        "https://android.googlesource.com/platform/packages/apps/PackageInstaller/",
    ),
    (
        "Phone",
        "https://android.googlesource.com/platform/packages/apps/Phone/",
    ),
    (
        "PhoneCommon",
        "https://android.googlesource.com/platform/packages/apps/PhoneCommon/",
    ),
    (
        "Protips",
        "https://android.googlesource.com/platform/packages/apps/Protips/",
    ),
    (
        "Provision",
        "https://android.googlesource.com/platform/packages/apps/Provision/",
    ),
    (
        "QuickAccessWallet",
        "https://android.googlesource.com/platform/packages/apps/QuickAccessWallet/",
    ),
    (
        "QuickSearchBox",
        "https://android.googlesource.com/platform/packages/apps/QuickSearchBox/",
    ),
    (
        "RemoteProvisioner",
        "https://android.googlesource.com/platform/packages/apps/RemoteProvisioner/",
    ),
    (
        "RetailDemo",
        "https://android.googlesource.com/platform/packages/apps/RetailDemo/",
    ),
    (
        "SafetyRegulatoryInfo",
        "https://android.googlesource.com/platform/packages/apps/SafetyRegulatoryInfo/",
    ),
    (
        "SampleLocationAttribution",
        "https://android.googlesource.com/platform/packages/apps/SampleLocationAttribution/",  # noqa: E501
    ),
    (
        "SecureElement",
        "https://android.googlesource.com/platform/packages/apps/SecureElement/",
    ),
    (
        "Settings",
        "https://android.googlesource.com/platform/packages/apps/Settings/",
    ),
    (
        "SettingsIntelligence",
        "https://android.googlesource.com/platform/packages/apps/SettingsIntelligence/",
    ),
    (
        "SmartCardService",
        "https://android.googlesource.com/platform/packages/apps/SmartCardService/",
    ),
    (
        "SoundRecorder",
        "https://android.googlesource.com/platform/packages/apps/SoundRecorder/",
    ),
    (
        "SpareParts",
        "https://android.googlesource.com/platform/packages/apps/SpareParts/",
    ),
    (
        "SpeechRecorder",
        "https://android.googlesource.com/platform/packages/apps/SpeechRecorder/",
    ),
    (
        "Stk",
        "https://android.googlesource.com/platform/packages/apps/Stk/",
    ),
    (
        "StorageManager",
        "https://android.googlesource.com/platform/packages/apps/StorageManager/",
    ),
    (
        "Sync",
        "https://android.googlesource.com/platform/packages/apps/Sync/",
    ),
    (
        "Tag",
        "https://android.googlesource.com/platform/packages/apps/Tag/",
    ),
    (
        "Terminal",
        "https://android.googlesource.com/platform/packages/apps/Terminal/",
    ),
    (
        "connectivity",
        "https://android.googlesource.com/platform/packages/apps/Test/connectivity/",
    ),
    (
        "ThemePicker",
        "https://android.googlesource.com/platform/packages/apps/ThemePicker/",
    ),
    (
        "TimeZoneData",
        "https://android.googlesource.com/platform/packages/apps/TimeZoneData/",
    ),
    (
        "TimeZoneUpdater",
        "https://android.googlesource.com/platform/packages/apps/TimeZoneUpdater/",
    ),
    (
        "Traceur",
        "https://android.googlesource.com/platform/packages/apps/Traceur/",
    ),
    (
        "TV",
        "https://android.googlesource.com/platform/packages/apps/TV/",
    ),
    (
        "TvSettings",
        "https://android.googlesource.com/platform/packages/apps/TvSettings/",
    ),
    (
        "UnifiedEmail",
        "https://android.googlesource.com/platform/packages/apps/UnifiedEmail/",
    ),
    (
        "UniversalMediaPlayer",
        "https://android.googlesource.com/platform/packages/apps/UniversalMediaPlayer/",
    ),
    (
        "Updater",
        "https://android.googlesource.com/platform/packages/apps/Updater/",
    ),
    (
        "VideoEditor",
        "https://android.googlesource.com/platform/packages/apps/VideoEditor/",
    ),
    (
        "VoiceDialer",
        "https://android.googlesource.com/platform/packages/apps/VoiceDialer/",
    ),
    (
        "WallpaperPicker",
        "https://android.googlesource.com/platform/packages/apps/WallpaperPicker/",
    ),
    (
        "WallpaperPicker2",
        "https://android.googlesource.com/platform/packages/apps/WallpaperPicker2/",
    ),
]


@dataclass
class Source:
    apps: Set[str] = field(default_factory=set)
    langs: Set[str] = field(default_factory=set)


def main():
    download_sources()
    strings = defaultdict(Source)
    for app, lang, sentences in glob_read_strings_files():
        for sentence in sentences:
            strings[sentence].apps.add(app)
            strings[sentence].langs.add(lang)
    with open(RESULT, "w", encoding="utf-8") as fp:
        json.dump(
            dict(
                sorted(
                    (
                        string,
                        {"apps": sorted(source.apps), "langs": sorted(source.langs)},
                    )
                    for string, source in strings.items()
                )
            ),
            fp,
            ensure_ascii=False,
            indent=2,
        )


def download_sources():
    for _name, repo in APP_GIT_REPOS:
        folder = DOWNLOADS / Path(repo).name
        folder.parent.mkdir(parents=True, exist_ok=True)
        if not folder.exists():
            git("clone", "--depth", "1", repo, folder)


def glob_read_strings_files():
    for name, repo in APP_GIT_REPOS:
        folder = DOWNLOADS / Path(repo).name
        # Doc: https://developer.android.com/guide/topics/resources/string-resource
        for path in folder.glob("**/strings.xml"):
            lang = "en"
            if match := re.match(r".*values-([^/\\]*)", str(path)):
                lang = match.group(1)
            sentences = []
            tree = ET.parse(path)
            root = tree.getroot()
            for string in itertools.chain(
                root.findall(".//string"), root.findall(".//item")
            ):
                for xliff_g in string.findall(
                    "./{urn:oasis:names:tc:xliff:document:1.2}g"
                ):
                    # Replace placeholders with example value if provided, otherwise kill
                    xliff_g.text = xliff_g.attrib.get("example", "")
                s = "".join(string.itertext())
                # Unquote. Each string might have several quoted bits
                s = "".join(
                    part[1:-1] if part and (part[0] == part[-1] == '"') else
                    # Collapse whitespace in unquoted bits
                    re.sub(r"\s+", " ", part)
                    # Split string. The "delimiters" are quoted bits, that start
                    # and end with an unescaped double quote. There's a capturing
                    # group around the whole expression so that the delimiters
                    # are kept in the output.
                    for part in re.split(r'((?<!\\)"(?:[^"]|\\"|\n)*(?<!\\)")', s)
                )
                # Unescape various things
                s = re.sub(r"""\\([@?nt'"]|u[0-9A-Fa-f]{4})""", unescape, s)
                # Split by lines and strip each
                # We're only interested in continuous lines (no breaks) for
                # kerning measurement purposes.
                for line in s.split("\n"):
                    line = line.strip()
                    if line:
                        sentences.append(line)
            yield name, lang, sentences


def unescape(m):
    g = m.group(1)
    if g[0] == "u":
        return chr(int(g[1:], base=16))
    elif g == "n":
        return "\n"
    elif g == "t":
        return "\t"
    return g


def git(*args):
    """Execute the given git command and return the output."""
    return subprocess.check_output(["git", *args])


if __name__ == "__main__":
    main()