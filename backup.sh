#!/usr/bin/env bash
# One-shot backup script for the Travel CRM.
# Creates a timestamped tar.gz containing the SQLite DB, uploaded media, and .env.
# Run from the project root:   bash backup.sh
set -e

cd "$(dirname "$0")"

TS=$(date +%Y%m%d-%H%M%S)
OUT_DIR="backups"
OUT_FILE="$OUT_DIR/travelcrm-backup-$TS.tar.gz"

mkdir -p "$OUT_DIR"

FILES=()
[ -f db.sqlite3 ] && FILES+=("db.sqlite3")
[ -d media ]     && FILES+=("media")
[ -f .env ]      && FILES+=(".env")

if [ ${#FILES[@]} -eq 0 ]; then
  echo "Nothing to back up (no db.sqlite3, media/, or .env found)."
  exit 1
fi

tar -czvf "$OUT_FILE" "${FILES[@]}"

echo ""
echo "Backup written to: $OUT_FILE"
echo "Size:              $(du -h "$OUT_FILE" | cut -f1)"
echo ""
echo "To restore on a new server:"
echo "  1) git clone <repo> && cd travel-crm"
echo "  2) python3 -m venv .venv && source .venv/bin/activate"
echo "  3) pip install -r requirements.txt"
echo "  4) tar -xzvf travelcrm-backup-$TS.tar.gz"
echo "  5) python manage.py migrate"
echo "  6) python manage.py collectstatic --noinput"
