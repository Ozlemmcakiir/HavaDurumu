from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_dockerfile_python_ve_port():
    text = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "python:3.14.7-slim" in text  # Eğer Dockerfile'da 3.14.7 kalmasını istiyorsan bu kalsın
    assert "EXPOSE 8080" in text         # 8000 olan yeri 8080 ile değiştir


def test_helm_chart_adi_ve_imaj():
    chart = (ROOT / "charts/havadurumu/Chart.yaml").read_text(encoding="utf-8")
    values = (ROOT / "charts/havadurumu/values.yaml").read_text(encoding="utf-8")
    assert "name: havadurumu" in chart
    assert "repository: havadurumu" in values
    assert 'tag: "0.1.0"' in values
    assert "enabled: true" in values
    assert "havadurumu.localtest.me" in values
    assert "className: nginx" in values
    assert "catchAll: true" in values


def test_ci_yardimci_dosyalari():
    assert (ROOT / "requirements-dev.txt").is_file()
    assert (ROOT / "scripts/ci-test.sh").is_file()
    assert (ROOT / "scripts/open-demo.ps1").is_file()
    assert (ROOT / "scripts/azure-setup.ps1").is_file()
    assert (ROOT / "scripts/deploy-azure.ps1").is_file()
    assert (ROOT / "scripts/azure.env.example").is_file()
    assert (ROOT / "pytest.ini").is_file()
