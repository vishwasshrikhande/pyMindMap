import json

from pymindmap.cli import main


def test_new_creates_file(tmp_path, capsys):
    path = tmp_path / "demo.mindmap.json"
    rc = main(["new", str(path), "--title", "My Map"])
    assert rc == 0
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["title"] == "My Map"


def test_show_tree_format(tmp_path, capsys):
    path = tmp_path / "demo.mindmap.json"
    main(["new", str(path), "--title", "My Map"])
    capsys.readouterr()

    rc = main(["show", str(path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "My Map" in out
    assert "Central Topic" in out


def test_show_json_format(tmp_path, capsys):
    path = tmp_path / "demo.mindmap.json"
    main(["new", str(path)])
    capsys.readouterr()

    rc = main(["show", str(path), "--format", "json"])
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert data["format"] == "pymindmap"


def test_validate_valid_file(tmp_path, capsys):
    path = tmp_path / "demo.mindmap.json"
    main(["new", str(path)])
    capsys.readouterr()

    rc = main(["validate", str(path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "OK" in out


def test_validate_corrupt_file_returns_error_exit_code(tmp_path, capsys):
    path = tmp_path / "corrupt.mindmap.json"
    path.write_text("{not valid json")

    rc = main(["validate", str(path)])
    err = capsys.readouterr().err
    assert rc == 1
    assert "Error" in err


def test_add_appends_node(tmp_path):
    path = tmp_path / "demo.mindmap.json"
    main(["new", str(path)])

    rc = main(["add", str(path), "--title", "New Idea", "--color", "#FF0000"])
    assert rc == 0

    data = json.loads(path.read_text())
    child = data["root"]["children"][0]
    assert child["title"] == "New Idea"
    assert child["style"]["fill_color"] == "#FF0000"


def test_convert_json_to_mm_and_back(tmp_path):
    json_path = tmp_path / "demo.mindmap.json"
    mm_path = tmp_path / "demo.mm"
    roundtrip_path = tmp_path / "demo2.mindmap.json"

    main(["new", str(json_path), "--title", "Round Trip"])
    rc1 = main(["convert", str(json_path), "--to", "mm", "-o", str(mm_path)])
    rc2 = main(["convert", str(mm_path), "--to", "json", "-o", str(roundtrip_path)])

    assert rc1 == 0
    assert rc2 == 0
    data = json.loads(roundtrip_path.read_text())
    assert data["root"]["title"] == "Central Topic"


def test_convert_to_markdown(tmp_path):
    json_path = tmp_path / "demo.mindmap.json"
    md_path = tmp_path / "demo.md"
    main(["new", str(json_path), "--title", "Root"])

    rc = main(["convert", str(json_path), "--to", "md", "-o", str(md_path)])

    assert rc == 0
    assert md_path.read_text().startswith("- Central Topic")
