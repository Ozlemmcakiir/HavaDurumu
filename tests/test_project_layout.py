from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_python_ve_port():
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "python:3.14.7-slim" in text
    assert "EXPOSE 8000" in text
    assert "main.py" in text


def test_helm_chart_adi_ve_imaj():
    chart = (ROOT / "charts/havadurumu/Chart.yaml").read_text(encoding="utf-8")
    values = (ROOT / "charts/havadurumu/values.yaml").read_text(encoding="utf-8")
    assert "name: havadurumu" in chart
    assert "repository: havadurumu" in values
    assert 'tag: "0.1.0"' in values


def test_ci_yardimci_dosyalari():
    assert (ROOT / "requirements-dev.txt").is_file()
    assert (ROOT / "scripts/ci-test.sh").is_file()
    assert (ROOT / "pytest.ini").is_file()
