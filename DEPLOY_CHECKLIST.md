# Deployment Checklist -- GitHub Repo Setup + Push Guide

Run these steps in order to deploy termux-whale-repo to GitHub Pages.

## Phase 0: Prerequisites

  winget install --id GitHub.cli      (or: sudo apt install gh)
  gh auth login
  gh auth status

## Phase 1: Init and Create Repo

  cd C:\Users\Carbon\projects\whaletermux
  gh repo create termux-whale-repo --public --source=. --remote=origin --push

## Phase 2: Stage, Commit and Push (if not done above)

  git add .
  git commit -m "feat: initial termux-whale-repo APT repository"
  git push -u origin main

## Phase 3: Enable GitHub Pages

Web UI: Repo > Settings > Pages > Source: GitHub Actions > Save

Or via CLI:
  gh api -X POST "/repos/YOUR_USERNAME/termux-whale-repo/pages" -f source[branch]="gh-pages" -f source[path]="/"

## Phase 4: Verify

  curl -s -o /dev/null -w "%%{http_code}" https://YOUR_USERNAME.github.io/termux-whale-repo/install.sh
  # Expected: 200

  curl -s -o /dev/null -w "%%{http_code}" https://YOUR_USERNAME.github.io/termux-whale-repo/dists/stable/Release
  # Expected: 200
