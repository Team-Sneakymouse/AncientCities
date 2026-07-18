#!/usr/bin/env bash
# Zip the datapack and upload it to the sandbox server (SFTP).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
else
  echo "Missing .env — copy .env.example to .env and fill in values." >&2
  exit 1
fi

: "${DEPLOY_HOST:?}"
: "${DEPLOY_PORT:?}"
: "${DEPLOY_USER:?}"
: "${DEPLOY_SSH_KEY:?}"
: "${DEPLOY_REMOTE_PATH:?}"
: "${DEPLOY_PACK_NAME:?}"

if [[ ! -f "$DEPLOY_SSH_KEY" ]]; then
  echo "SSH key not found: $DEPLOY_SSH_KEY" >&2
  exit 1
fi

if [[ "$DEPLOY_SSH_KEY" == *.ppk ]]; then
  echo "DEPLOY_SSH_KEY is a PuTTY .ppk file; OpenSSH needs an OpenSSH key." >&2
  echo "Use the converted key (e.g. ${DEPLOY_SSH_KEY%.ppk}) or:" >&2
  echo "  puttygen \"$DEPLOY_SSH_KEY\" -O private-openssh -o \"${DEPLOY_SSH_KEY%.ppk}\"" >&2
  exit 1
fi

DIST="$ROOT/dist"
ZIP_NAME="${DEPLOY_PACK_NAME}.zip"
ZIP="$DIST/$ZIP_NAME"
mkdir -p "$DIST"

echo "Building $ZIP ..."
rm -f "$ZIP"
# Datapack root must contain pack.mcmeta (no wrapping folder).
zip -r "$ZIP" pack.mcmeta data INSTALL.md \
  -x "*.DS_Store" \
  -x "*__MACOSX*"

REMOTE_FILE="${DEPLOY_REMOTE_PATH%/}/$ZIP_NAME"
echo "Uploading to ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PORT}:${REMOTE_FILE} ..."

# Sandbox is SFTP-only (no shell). scp often returns -1 even on success; use sftp.
sftp -P "$DEPLOY_PORT" \
  -i "$DEPLOY_SSH_KEY" \
  -o IdentitiesOnly=yes \
  -o StrictHostKeyChecking=accept-new \
  "${DEPLOY_USER}@${DEPLOY_HOST}" <<EOF
put $ZIP $REMOTE_FILE
ls -l $REMOTE_FILE
bye
EOF

echo "Done: $REMOTE_FILE"
