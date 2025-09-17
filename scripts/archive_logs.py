import argparse
import datetime as dt
import os
from pathlib import Path
import zipfile


def find_log_roots(base: Path) -> list[Path]:
    candidates = []
    for name in ("05-LOGS", "04-DATA/logs", "data/logs"):
        p = base / name
        if p.exists():
            candidates.append(p)
    return candidates


def iter_log_files(root: Path, date_str: str):
    patterns = ["*.log", "*.log.*", f"*_{date_str}.ndjson", "*.ndjson"]
    for pattern in patterns:
        for path in root.rglob(pattern):
            # Skip empty files
            try:
                if path.is_file() and path.stat().st_size > 0:
                    yield path
            except FileNotFoundError:
                continue


def archive_logs(base_dir: Path, out_dir: Path, date: dt.date, include_all_ndjson: bool = False) -> Path:
    date_str = date.strftime("%Y-%m-%d")
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"logs_{date_str}.zip"

    log_roots = find_log_roots(base_dir)
    if not log_roots:
        raise FileNotFoundError("No se hallaron carpetas de logs esperadas")

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root in log_roots:
            for f in iter_log_files(root, date_str):
                if f.suffix == ".ndjson" and not include_all_ndjson:
                    # Por defecto empaquetar solo ndjson del día
                    if not f.name.endswith(f"_{date_str}.ndjson"):
                        continue
                arcname = f.relative_to(base_dir)
                zf.write(f, arcname.as_posix())

    return zip_path


def main():
    parser = argparse.ArgumentParser(description="Archiva logs y NDJSON del día en un ZIP listo para IA")
    parser.add_argument("--date", help="Fecha a archivar (YYYY-MM-DD). Por defecto hoy.")
    parser.add_argument("--base", help="Ruta base del proyecto. Por defecto cwd.")
    parser.add_argument("--out", help="Directorio de salida. Por defecto 04-DATA/exports/logs")
    parser.add_argument("--all-ndjson", action="store_true", help="Incluir todos los .ndjson, no solo los del día")
    args = parser.parse_args()

    date = dt.date.today() if not args.date else dt.date.fromisoformat(args.date)
    base_dir = Path(args.base).resolve() if args.base else Path(os.getcwd()).resolve()
    out_dir = Path(args.out).resolve() if args.out else (base_dir / "04-DATA" / "exports" / "logs").resolve()

    zip_path = archive_logs(base_dir, out_dir, date, include_all_ndjson=args.all_ndjson)
    print(f"Archivo generado: {zip_path}")


if __name__ == "__main__":
    main()
