import textwrap

import follow_up


def test_email_drafting_for_sample_follow_up(tmp_path, capsys):
    csv_path = tmp_path / "followups.csv"
    csv_path.write_text(
        textwrap.dedent(
            """\
            id,contact_name,contact_email,company,topic,last_contact_date,due_date,status,notes
            1,Ayesha Khan,ayesha@example.com,Northwind Traders,Delivery schedule confirmation,2026-10-15,2026-10-20,open,Waiting on final delivery slots
            """
        ),
        encoding="utf-8",
    )

    exit_code = follow_up.main(
        ["--input", str(csv_path), "--as-of", "2026-10-27"]
    )

    assert exit_code == 0
    stdout = capsys.readouterr().out
    assert "# Follow-up drafts — as of 2026-10-27" in stdout
    assert "## Draft 1 (overdue)" in stdout
    assert "To: ayesha@example.com" in stdout
    assert (
        "Subject: Follow-up: Delivery schedule confirmation — Northwind Traders"
        in stdout
    )
    assert "Summary: 1 overdue, 0 due soon, 0 skipped." in stdout
