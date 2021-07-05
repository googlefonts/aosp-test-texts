# Copyright 2021 Google LLC
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

"""Extract all sentences belonging to selected languages.

Useful when constructing example text. Only considers the base language, not
sublocale-specifiers.
"""

import argparse
import collections
import json
import tempfile
from pathlib import Path
from typing import Dict, List

parser = argparse.ArgumentParser()
parser.add_argument(
    "languages", nargs="+", help="ISO 639-1 language codes to extract sentences for."
)
parsed_args = parser.parse_args()

CORPUS = Path(__file__).parent.parent / "corpus" / "aosp.json"

with open(CORPUS) as f:
    data = json.load(f)

# NOTE: Android seems to use different local specifiers, so just use the bare language.
desired_languages = set(l.split("-")[0] for l in parsed_args.languages)
findings: Dict[str, List[str]] = collections.defaultdict(list)

for sentence, info in data.items():
    languages = set(l.split("-")[0] for l in info["langs"])
    for l in languages:
        if l in desired_languages:
            findings[l].append(sentence)

TEMP_DIR = Path(tempfile.gettempdir())

for language, sentences in findings.items():
    target_path = TEMP_DIR / f"sentences-{language}.txt"
    with open(target_path, "w+") as f:
        f.write("\n".join(sorted(sentences)))
    print(f"Wrote {str(target_path)}")
