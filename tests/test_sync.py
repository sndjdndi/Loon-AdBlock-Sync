import tempfile
import unittest
from pathlib import Path
from sync import SyncError, parse, render, check_retention, upstream_metadata


class ConversionTests(unittest.TestCase):
    def test_all_five_kinds(self):
        source = """HOST,ad.example.com,REJECT
HOST-SUFFIX,ads.example.com,REJECT
HOST-KEYWORD,tracking,REJECT
IP-CIDR,192.0.2.0/24,REJECT,no-resolve
IP6-CIDR,2001:db8::/32,REJECT
HOST,ad.example.com,REJECT
"""
        self.assertEqual(parse(source, "sample", 1), [
            "DOMAIN,ad.example.com",
            "DOMAIN-SUFFIX,ads.example.com",
            "DOMAIN-KEYWORD,tracking",
            "IP-CIDR,192.0.2.0/24,no-resolve",
            "IP-CIDR6,2001:db8::/32",
        ])

    def test_unknown_type_fails(self):
        with self.assertRaises(SyncError):
            parse("URL-REGEX,^https,REJECT", "test", 1)

    def test_direct_fails(self):
        with self.assertRaises(SyncError):
            parse("HOST,ads.test,DIRECT", "test", 1)

    def test_no_rules_fails(self):
        for html in ("", "<html>Failure</html>", "<!doctype html>"):
            with self.subTest(html=html), self.assertRaises(SyncError):
                parse(html, "test", 1)

    def test_invalid_ip_version_fails(self):
        with self.assertRaises(SyncError):
            parse("IP6-CIDR,192.0.2.0/24,REJECT", "test", 1)

    def test_unsupported_flag_fails(self):
        with self.assertRaises(SyncError):
            parse("HOST,ad.test,REJECT,unsupported", "test", 1)

    def test_rule_floor(self):
        with self.assertRaises(SyncError):
            parse("HOST,ad.test,REJECT", "test", 2)

    def test_retention_protection(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "source.list"
            path.write_text("".join(f"DOMAIN,ad{i}.test\n" for i in range(100)))
            with self.assertRaises(SyncError):
                check_retention(path, [f"DOMAIN,ad{i}.test" for i in range(30)])

    def test_stable_output_and_attribution(self):
        meta = {"NAME": "sample", "AUTHOR": "Test Author", "UPDATED": "2026-10-19 06:20:23 (UTC+8)", "DESC": "开屏广告专项"}
        a = render("sample", ["DOMAIN,ad.test"], meta)
        self.assertEqual(a, render("sample", ["DOMAIN,ad.test"], meta))
        self.assertIn("LICENSE", a)
        self.assertIn("REJECT", a)
        self.assertIn("# 上游更新时间: 2026-10-19 06:20:23 (UTC+8)", a)
        self.assertIn("每 12 小时", a)

    def test_source_metadata(self):
        data = "# NAME: sample\\n# AUTHOR: Test Author\\n# UPDATED: 2026-10-19 06:20:23 (UTC+8)\\n# DESC: 开屏广告专项\\n"
        data = data.replace("\\\\n", "\\n")
        meta = upstream_metadata(data, "sample")
        self.assertEqual(meta["UPDATED"], "2026-10-19 06:20:23 (UTC+8)")
        with self.assertRaises(SyncError):
            upstream_metadata("# NAME: sample", "sample")


if __name__ == "__main__":
    unittest.main()
