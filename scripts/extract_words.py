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

import json
from collections import defaultdict
from pathlib import Path

CORPUS = Path(__file__).parent.parent / "corpus" / "aosp.json"


def main() -> None:
    data = json.loads(CORPUS.read_text(encoding="utf-8"))

    # Lang -> words
    lang_words: dict[str, set[str]] = defaultdict(set)

    for sentence, info in data.items():
        words = [word.strip() for word in sentence.split() if word.strip() != ""]
        languages = set(lang.split("-")[0] for lang in info["langs"])
        for language in languages:
            lang_words[language].update(words)
    
    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    for language, words in lang_words.items():
        out_file = out_dir / f"{language}.txt"
        out_file.write_text("\n".join(sorted(words)) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
