from scripts.check_public_release import Finding, content_findings, load_publicignore, path_denials


def test_load_publicignore_expands_directory_patterns(tmp_path) -> None:
    publicignore = tmp_path / ".publicignore"
    publicignore.write_text("# comment\noutput/\nconductor/slice-*.md\n", encoding="utf-8")

    assert load_publicignore(str(publicignore)) == ["output/*", "conductor/slice-*.md"]


def test_path_denials_flags_private_conductor_files() -> None:
    findings = path_denials(
        [
            "README.md",
            "conductor/handoff-log.md",
            "conductor/slice-06-public-release-flow.md",
        ],
        ["conductor/handoff-log.md", "conductor/slice-*.md"],
    )

    assert findings == [
        Finding(
            "error",
            "conductor/handoff-log.md",
            "matches private path rule `conductor/handoff-log.md`",
        ),
        Finding(
            "error",
            "conductor/slice-06-public-release-flow.md",
            "matches private path rule `conductor/slice-*.md`",
        ),
    ]


def test_content_findings_flags_local_paths(monkeypatch) -> None:
    def fake_read_file_at_ref(ref: str, path: str) -> str:
        assert ref == "HEAD"
        assert path == "docs/public-release.md"
        return "workspace: /" + "Volumes/t9/dev/tools/strata\n"

    monkeypatch.setattr("scripts.check_public_release.read_file_at_ref", fake_read_file_at_ref)

    assert content_findings("HEAD", ["docs/public-release.md"]) == [
        Finding("error", "docs/public-release.md", "contains local machine path")
    ]
