import unittest

from body import HEADINGS, template

REPO = "Casper-Studios/casper-secret-sauce"
PATH = "plugins/hr/candidate-evaluation/skills/a-skill/SKILL.md"


def text_of(block):
    return "".join(part["text"]["content"] for part in block[block["type"]]["rich_text"])


class TemplateTest(unittest.TestCase):
    def test_install_then_headings_then_source(self):
        blocks = template("a-skill", REPO, PATH)
        self.assertEqual([b["type"] for b in blocks[:2]], ["heading_2", "code"])
        self.assertEqual(text_of(blocks[0]), "How to Install")
        self.assertEqual(text_of(blocks[1]), f"npx skills add https://github.com/{REPO} --skill a-skill")
        self.assertEqual(blocks[1]["code"]["language"], "bash")
        middle = blocks[2 : 2 + len(HEADINGS)]
        self.assertEqual([(b["type"], text_of(b)) for b in middle], HEADINGS)
        self.assertEqual(text_of(blocks[-2]), "Source")
        link = blocks[-1]["paragraph"]["rich_text"][0]["text"]
        self.assertEqual(link["link"], {"url": f"https://github.com/{REPO}/blob/main/{PATH}"})

    def test_every_block_is_a_block(self):
        for block in template("a-skill", REPO, PATH):
            self.assertEqual(block["object"], "block")
            self.assertIn(block["type"], block)

    def test_no_prose_is_invented(self):
        texts = [text_of(b) for b in template("a-skill", REPO, PATH)]
        self.assertEqual(len(texts), 2 + len(HEADINGS) + 2)
        self.assertTrue(all(len(t) < 120 for t in texts))


if __name__ == "__main__":
    unittest.main()
