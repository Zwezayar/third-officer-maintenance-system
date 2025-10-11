#!/usr/bin/env bash
set -euo pipefail

# Project folders
REPO=~/third-officer-maintenance-system
DATA="$REPO/backend/data"

echo ">> Ensure backend/data exists"
mkdir -p "$DATA"

# Source files (edit these if your filenames are different)
HANDOVER_SRC=~/Downloads/"YI - (V-185) Third Officers Handover Note.doc"
LSA_SRC=~/Downloads/"Life-Saving Appliances Pocket Checklist.pdf"
FFA_SRC=~/Downloads/"MARINE FIRE SAFETY POCKET CL.pdf"
NK_SRC=~/Downloads/"Class NK - Good_Maintenance_Onboard.pdf"

# Copy files to backend/data
[ -f "$HANDOVER_SRC" ] && cp -v "$HANDOVER_SRC" "$DATA/" || echo " - Handover DOC not found"
[ -f "$LSA_SRC" ] && cp -v "$LSA_SRC" "$DATA/" || echo " - LSA PDF not found"
[ -f "$FFA_SRC" ] && cp -v "$FFA_SRC" "$DATA/" || echo " - FFA PDF not found"
[ -f "$NK_SRC" ] && cp -v "$NK_SRC" "$DATA/" || echo " - NK PDF not found"

# Convert DOC -> MD
if [ -f "$DATA/$(basename "$HANDOVER_SRC")" ]; then
    pandoc "$DATA/$(basename "$HANDOVER_SRC")" -o "$DATA/handover_note.md"
    echo "Converted handover DOC to handover_note.md"
fi

# Convert PDFs -> TXT
for pdf in "$DATA/$(basename "$LSA_SRC")" "$DATA/$(basename "$FFA_SRC")" "$DATA/$(basename "$NK_SRC")"; do
    if [ -f "$pdf" ]; then
        txt="${pdf%.pdf}.txt"
        pdftotext "$pdf" "$txt"
        echo "Converted $pdf -> $txt"
    fi
done

# Quick previews
echo "---- Preview: LSA checklist ----"
head -n 20 "$DATA/lsa_checklist.txt" || true

echo "---- Preview: Handover note ----"
[ -f "$DATA/handover_note.md" ] && head -n 20 "$DATA/handover_note.md" || echo "(no handover_note.md)"

echo ">> Done! All files in $DATA"
ls -lh "$DATA"


