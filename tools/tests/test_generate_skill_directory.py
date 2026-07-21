from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

import generate_skill_directory


class SkillDirectoryGeneratorTests(unittest.TestCase):
    def test_renders_verified_external_reference_link(self) -> None:
        rows = generate_skill_directory.normalize_records(
            [
                {
                    "skill_id": "humanizer-zh",
                    "offices": "礼部",
                    "lifecycle": "active",
                    "source": "optional-interface",
                    "note": "Chinese editorial skill",
                }
            ],
            {
                "humanizer-zh": {
                    "source_relation": "external-reference",
                    "source_url": "https://github.com/op7418/Humanizer-zh",
                    "source_note": "Public upstream project",
                }
            },
        )

        page = generate_skill_directory.render_page(rows, "en")

        self.assertIn("[Public upstream project](https://github.com/op7418/Humanizer-zh)", page)
        self.assertIn("humanizer-zh", page)
        self.assertIn("礼部", page)

    def test_rejects_unverifiable_external_reference(self) -> None:
        with self.assertRaisesRegex(ValueError, "External source requires HTTPS URL: unknown-skill"):
            generate_skill_directory.normalize_records(
                [
                    {
                        "skill_id": "unknown-skill",
                        "offices": "吏部",
                        "lifecycle": "active",
                        "source": "optional-interface",
                        "note": "Unknown source",
                    }
                ],
                {
                    "unknown-skill": {
                        "source_relation": "external-reference",
                        "source_url": None,
                        "source_note": "",
                    }
                },
            )


if __name__ == "__main__":
    unittest.main()
