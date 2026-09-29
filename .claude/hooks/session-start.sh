#!/usr/bin/env bash
# Prepares a Claude Code on the web session for Claude + Video Editing:
# ffmpeg/ffprobe for encoding and probing, and the HyperFrames agent skills.
set -euo pipefail

# Only run in remote (web) sessions; local machines manage their own tools.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

HF_VERSION="0.8.91"

if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    apt-get install -y -qq ffmpeg >/dev/null 2>&1 ||
      { apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq ffmpeg >/dev/null 2>&1; } ||
      echo "session-start: could not install ffmpeg" >&2
  fi
fi

# Core HyperFrames skills plus the motion-graphics workflow (the project's core feature).
npx -y "hyperframes@${HF_VERSION}" skills update motion-graphics >/dev/null 2>&1 ||
  echo "session-start: could not install HyperFrames skills" >&2

exit 0
