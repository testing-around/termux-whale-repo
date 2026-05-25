# Deployment Checklist -- GitHub Repo Setup + Push Guide

> GitHub username: **testing-around**
> Repo name: **termux-whale-repo**
> Git remote: ✅ Already configured

Run these steps in order to deploy to GitHub Pages.

---

## Phase 1: Create the Repo on GitHub.com

1. Go to https://github.com/new
2. Repository name: `termux-whale-repo`
3. Description: "Custom Termux APT repository for Whale Agent"
4. Public (not private)
5. DO NOT add README, .gitignore, or license
6. Click "Create repository"

---

## Phase 2: Push the Code

```bash
cd C:\Users\Carbon\projects\whaletermux
git push -u origin main
```

Expected output:
```
Enumerating objects: ...
Writing objects: ...
To https://github.com/testing-around/termux-whale-repo.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

## Phase 3: Enable GitHub Pages

1. Go to: https://github.com/testing-around/termux-whale-repo/settings/pages
2. Under "Source", select **GitHub Actions**
3. No branch selection needed -- the existing `.github/workflows/deploy.yml` handles it
4. The CI/CD workflow will auto-run and deploy the APT repo

Check workflow status: https://github.com/testing-around/termux-whale-repo/actions

---

## Phase 4: Verify Deployment

```bash
curl -s -o /dev/null -w "HTTP %{http_code}" https://testing-around.github.io/termux-whale-repo/install.sh
# Expected: 200

curl -s -o /dev/null -w "HTTP %{http_code}" https://testing-around.github.io/termux-whale-repo/dists/stable/Release
# Expected: 200
```

---

## Phase 5: Install on Termux

```bash
curl -sL https://testing-around.github.io/termux-whale-repo/install.sh | bash
whale --version
```
