# Loon-AdBlock-Sync

Automatically sync and convert three lists from [hwind2021/QuantumultX-AdBlock-CN](https://github.com/hwind2021/QuantumultX-AdBlock-CN) into native, policy-free **Loon remote rule** lists.

## Feeds

| Output | Upstream | Expected baseline count (2026-10-19) |
| --- | --- | ---: |
| `loon/Splash-Killer.list` | `quantumultx/filter/Splash-Killer.list` | 473 |
| `loon/BlockHttpDNS.list` | `quantumultx/filter/BlockHttpDNS.list` | 62 |
| `loon/AdBlock-Lite.list` | `quantumultx/filter/AdBlock-Lite.list` | 22,739 |

The output files are generated automatically after the first successful workflow run. Do not edit them manually.

## Installation in Loon

1. Run the GitHub Actions workflow **Sync QX AdBlock to Loon** once with `Run workflow`.
2. In Loon, go to **Remote Rule**, add one of the following Raw URLs, and set its **policy to `REJECT`**:

   - `https://raw.githubusercontent.com/sndjdndi/Loon-AdBlock-Sync/main/loon/Splash-Killer.list`
   - `https://raw.githubusercontent.com/sndjdndi/Loon-AdBlock-Sync/main/loon/BlockHttpDNS.list`
   - `https://raw.githubusercontent.com/sndjdndi/Loon-AdBlock-Sync/main/loon/AdBlock-Lite.list`

3. These are **remote rules, not plugins**. Do **not** paste them into the Loon Plugin page. They do **not** require MITM.
4. Usually enable **AdBlock-Lite alone first**. It incorporates splash and HTTPDNS filtering, and overlaps with the separate lists. Avoid using it concurrently with other broad filters (AWAvenue, AdRules or 217heidai Lite) until you have a reason and can troubleshoot conflicts.
5. Keep original upstream attribution. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Synchronization

- GitHub Actions checks upstream every four hours (`17 */4 * * *`, UTC); exact timing is best effort.
- It also supports manually running `workflow_dispatch`.
- All three source files must download and validate before any generated file is changed.
- Unknown QX syntax, non-REJECT policies, invalid IP address formats, unexpectedly low rule counts or drops of more than 35% versus an existing generated file will **fail the job without a Git commit**.
- No generated timestamp is inserted, so identical input results in no commit.
- Requirements: Python 3.10+ standard library only.

## Develop / test

```sh
python3 -m unittest discover -s tests -v
python3 sync.py --dry-run
python3 sync.py
```

`--dry-run` still downloads all live feeds and validates against any existing output, but writes nothing. A successful live run requires internet access to GitHub Raw.

## Notes and limitations

- This project converts **filter rules only**. It does not transform Quantumult X rewrite scripts or MITM configurations.
- A new upstream rule type fails closed rather than silently disappearing. Review before extending the converter.
- Blocking HTTPDNS may break name resolution or connectivity of some apps; disable that feed if encountered.
- Automatic regeneration does not independently verify that upstream advertising signatures remain effective for current app versions.
- A public GitHub repository makes these Raw subscription URLs accessible without authentication.
- New GitHub repositories may need GitHub Actions enabled; review the repository's **Settings > Actions > General > Workflow permissions** if commits fail with permission errors. Public-repo inactivity can disable scheduled runs.

## Attribution

This conversion project is separate from and not endorsed by hwind2021/QuantumultX-AdBlock-CN. All source rules and attribution belong to their respective authors. See `THIRD_PARTY_NOTICES.md`.