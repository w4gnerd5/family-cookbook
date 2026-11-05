#!/usr/bin/env bash
# Cut a release of the book: build both PDF editions, tag v<version>, publish
# a GitHub Release with the two PDFs attached.
#
#   scripts/release.sh            full release
#   scripts/release.sh --dry-run  build both editions into dist/, publish nothing
#
# Before running: bump `version:` in book.yaml, add a matching "## <version>"
# section to CHANGELOG.md, commit, push.
#
# Asset names never change between releases, so these URLs always serve the
# newest edition (they are what the README links to):
#   https://github.com/w4gnerd5/family-cookbook/releases/latest/download/cookbook-screen.pdf
#   https://github.com/w4gnerd5/family-cookbook/releases/latest/download/cookbook-print.pdf
# Releases are never flagged as pre-release: GitHub's "latest" skips those,
# which would break the links. The 0.x version number marks pre-1.0 instead.

set -euo pipefail
cd "$(dirname "$0")/.."

DRY=0
[[ "${1:-}" == "--dry-run" ]] && DRY=1

die() { echo "release: $*" >&2; exit 1; }

VERSION=$(sed -n 's/^version:[[:space:]]*\([0-9][0-9.]*\).*/\1/p' book.yaml)
[[ -n "$VERSION" ]] || die "no version: in book.yaml"
TAG="v$VERSION"

grep -q "^## $VERSION " CHANGELOG.md || die "CHANGELOG.md has no '## $VERSION' section"
NOTES=$(awk -v v="$VERSION" '
  $0 ~ "^## " v " " {on=1; next}
  on && /^## /      {exit}
  on                {print}' CHANGELOG.md)
NOTES="**Which file?** \`cookbook-screen.pdf\` is for reading on a phone, tablet or
computer. \`cookbook-print.pdf\` is the full-resolution file for a print shop
(A4 with 3mm bleed); it is very large.

$NOTES"

if (( ! DRY )); then
  [[ -z "$(git status --porcelain)" ]] || die "working tree not clean"
  [[ "$(git branch --show-current)" == "main" ]] || die "not on main"
  git fetch -q origin
  [[ "$(git rev-parse HEAD)" == "$(git rev-parse origin/main)" ]] \
    || die "main is not in sync with origin/main; push or pull first"
  git rev-parse -q --verify "refs/tags/$TAG" >/dev/null && die "tag $TAG already exists"
  git ls-remote --exit-code --tags origin "$TAG" >/dev/null && die "tag $TAG already on origin"
fi

echo "== building $TAG"
python3 scripts/md_to_data.py
python3 scripts/make_cards.py
typst compile --root . --font-path assets/fonts print/cookbook.typ print/cookbook.pdf

if (( ! DRY )); then
  [[ -z "$(git status --porcelain)" ]] \
    || die "the build changed tracked files; commit the rebuilt outputs first"
fi

mkdir -p dist
cp print/cookbook.pdf dist/cookbook-print.pdf
echo "== compressing screen edition (takes a few minutes)"
gs -q -dNOPAUSE -dBATCH -dSAFER -sDEVICE=pdfwrite -dCompatibilityLevel=1.7 \
   -dPDFSETTINGS=/ebook -dDetectDuplicateImages=true \
   -dColorImageResolution=150 -dGrayImageResolution=150 \
   -sOutputFile=dist/cookbook-screen.pdf dist/cookbook-print.pdf

pages() { pdfinfo "$1" | awk '/^Pages:/ {print $2}'; }
P1=$(pages dist/cookbook-print.pdf); P2=$(pages dist/cookbook-screen.pdf)
[[ "$P1" == "$P2" ]] || die "page count mismatch: print $P1, screen $P2"
ls -lh dist/*.pdf
echo "== $P1 pages each"

if (( DRY )); then
  echo "== dry run: nothing tagged or published"
  exit 0
fi

git tag -a "$TAG" -m "Cookbook $TAG"
git push origin "$TAG"
gh release create "$TAG" dist/cookbook-screen.pdf dist/cookbook-print.pdf \
  --title "Family Cookbook $TAG" --notes "$NOTES" --latest
echo "== published $TAG"
