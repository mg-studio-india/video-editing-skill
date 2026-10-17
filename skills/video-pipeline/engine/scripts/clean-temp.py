#!/usr/bin/env python3
"""clean-temp.py: Safely removes transient scratch files, intermediate audio stems,
temporary whisper dumps, and un-mastered raw video renders from a project directory,
preserving essential deliverables, master compositions, and project state.

Usage:
  python3 clean-temp.py videos/<project> [--dry-run] [--verbose]
"""
import argparse, os, glob, shutil

TRANSIENT_PATTERNS = [
    # Transient audio files
    "audio-raw.wav",
    "audio.wav",
    "audio-clean.wav",
    "tmp_*.wav",
    "raw/*_temp.*",
    "raw/*_enhanced.m4a",
    "raw/*_muted.mp4",
    "raw/*_combined.mp4",
    # Auto-editor and candidate dumps
    "speech.v1",
    "speech.json",
    "candidates",
    "cut-candidates",
    "*.log",
    # Intermediate raw video before mastering/tagging
    "processed/*-raw.mp4",
    "processed/*-temp.mp4",
    "processed/*-tagged.mp4",
    "output/*-raw.mp4",
    "output/*-temp.mp4",
    "output/*-tagged.mp4",
    "hyperframes/tmp_*",
    "hyperframes/frame_*.png",
    "public/tmp_*",
    "public/frame_*.png"
]

REPORT_PATTERNS = [
    "processed/*-VERIFY.md",
    "processed/*-REVIEW.md",
    "processed/*-audio.json",
    "processed/*-review-sheet.png",
    "output/*-VERIFY.md",
    "output/*-REVIEW.md",
    "output/*-audio.json",
    "output/*-review-sheet.png",
]

def clean_project(project_dir, dry_run=False, verbose=True, clean_reports=False):
    project_dir = os.path.abspath(project_dir)
    if not os.path.isdir(project_dir):
        print(f"Error: Project directory not found: {project_dir}")
        return 1

    total_bytes_freed = 0
    removed_count = 0

    print(f"🧹 Cleaning transient files in: {project_dir}" + (" (including review reports)" if clean_reports else ""))
    if dry_run:
        print("  (DRY RUN - no files will be deleted)")

    patterns = TRANSIENT_PATTERNS + (REPORT_PATTERNS if clean_reports else [])
    for pattern in patterns:
        matches = glob.glob(os.path.join(project_dir, pattern))
        for p in matches:
            # Safety checks: never delete the final deliverable or master composition
            base = os.path.basename(p)
            if base in ["input-video.mp4", "index.html", "storyboard.json", "style.json", "project.json"]:
                continue
            if not clean_reports and (base.endswith("-REVIEW.md") or base.endswith("-VERIFY.md") or base.endswith("-audio.json") or base.endswith("-review-sheet.png")):
                continue

            try:
                if os.path.isfile(p) or os.path.islink(p):
                    sz = os.path.getsize(p)
                    if not dry_run:
                        os.remove(p)
                    total_bytes_freed += sz
                    removed_count += 1
                    if verbose:
                        print(f"  - Removed file: {os.path.relpath(p, project_dir)} ({sz / (1024*1024):.2f} MB)")
                elif os.path.isdir(p):
                    sz = sum(os.path.getsize(os.path.join(root, f)) for root, _, files in os.walk(p) for f in files)
                    if not dry_run:
                        shutil.rmtree(p)
                    total_bytes_freed += sz
                    removed_count += 1
                    if verbose:
                        print(f"  - Removed directory: {os.path.relpath(p, project_dir)} ({sz / (1024*1024):.2f} MB)")
            except Exception as e:
                print(f"  ! Warning: could not remove {p}: {e}")

    mb_freed = total_bytes_freed / (1024 * 1024)
    print(f"✨ Cleanup complete: {removed_count} items removed, {mb_freed:.2f} MB space reclaimed.")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean temporary video editing artifacts.")
    parser.add_argument("project", help="Path to video project directory")
    parser.add_argument("--dry-run", action="store_true", help="Simulate deletion without removing files")
    parser.add_argument("--clean-reports", action="store_true", help="Delete verification reports and review sheets after successful review")
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed file listings")
    args = parser.parse_args()

    clean_project(args.project, dry_run=args.dry_run, verbose=not args.quiet, clean_reports=args.clean_reports)
