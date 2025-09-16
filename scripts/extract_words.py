# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import csv
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import cast

import youseedee
from gflanguages import LoadLanguages, LoadScripts

CLDR_SCRIPT_TO_UCD_SCRIPT = {
    "Bangla": "Bengali",
    "Traditional Han": "Han",
    "Simplified Han": "Han",
    "Korean": "Hangul",
    "Odia": "Oriya",
    "Makasar": "Buginese",
    "Lanna": "Tai Tham",
    "Unified Canadian Aboriginal Syllabics": "Canadian Aboriginal",
    "S-A Cuneiform": "Cuneiform",
    "Pollard Phonetic": "Miao",
    "Egyptian hieroglyphs": "Egyptian Hieroglyphs",
    "Zanabazar": "Zanabazar Square",
    "Nüshu": "Nushu",
    "Mandaean": "Mandaic",
    "N’Ko": "Nko",
    "Varang Kshiti": "Warang Citi",
    "Mende": "Mende Kikakui",
    "Phags-pa": "Phags Pa",
    "Fraser": "Lisu",
    "Georgian Khutsuri": "Georgian",
    "Orkhon": "Old Turkic",
}

CORPUS = Path(__file__).parent.parent / "corpus" / "aosp.json"
LANGUAGES = LoadLanguages().values()
SCRIPTS = LoadScripts()

scripts_per_lang: dict[str, set[str]] = defaultdict(set)

SCRIPT_TAGS = {}
with open(
    os.path.join(youseedee.ucd_dir(), "PropertyValueAliases.txt"), "r", encoding="utf-8"
) as f:
    reader = csv.reader(f, delimiter=";", skipinitialspace=True)
    for row in reader:
        if len(row) >= 3 and row[0].strip() == "sc":
            SCRIPT_TAGS[row[2].strip()] = row[1].strip()

for lang in LANGUAGES:
    script_name = SCRIPTS[lang.script].name
    script_name = CLDR_SCRIPT_TO_UCD_SCRIPT.get(script_name, script_name)
    scripts_per_lang[lang.language].add(script_name)


def itemize_by_script(text, scripts):
    itemized = defaultdict(str)
    for char in text:
        char_script = youseedee.ucd_data(ord(char)).get("Script")
        if char_script == "Common" or char_script == "Inherited" or not char_script:
            continue
        char_script = char_script.replace("_", " ")
        if char_script not in scripts:
            continue
        itemized[SCRIPT_TAGS[char_script]] += char
    return itemized


def main() -> None:
    data = json.loads(CORPUS.read_text(encoding="utf-8"))

    # Lang -> words
    lang_words: dict[str, set[str]] = defaultdict(set)

    for sentence, info in data.items():
        sentence = cast(str, sentence)

        words = set()
        for word in sentence.split():
            word = word.strip()
            if word != "":
                words.add(word)

        languages = set()
        for language_string in info["langs"]:
            language = language_string.split("-")[0]
            if len(language) == 2:
                languages.add(language)

        for language in languages:
            if language in scripts_per_lang:
                for word in words:
                    for script, itemized in itemize_by_script(
                        word, scripts_per_lang[language]
                    ).items():
                        if not itemized:
                            continue
                        lang_words[language + "_" + script].add(itemized)
            else:
                lang_words[language].update(words)

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    for tag, words in lang_words.items():
        out_file = out_dir / f"{tag}.txt"
        out_file.write_text("\n".join(sorted(words)) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
