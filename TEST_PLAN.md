# Test Plan -- Termux End-to-End Validation

Test on a real Android device after deployment.

## Prerequisites

- [ ] Android 7.0+ with Termux (from F-Droid)
- [ ] Internet connection
- [ ] Repo deployed to GitHub Pages

## Test 1: Repo Registration

  echo "deb [trusted=yes] https://YOUR_USERNAME.github.io/termux-whale-repo stable main" > $PREFIX/etc/apt/sources.list.d/whale.list
  cat $PREFIX/etc/apt/sources.list.d/whale.list
  # Expected: deb [trusted=yes] https://... stable main

## Test 2: Package Installation

  pkg update         # whale repo should appear
  pkg install whale-agent   # installs v1.0.0
  pkg list-installed | grep whale   # shows whale-agent
  which whale        # /data/data/com.termux/files/usr/bin/whale

## Test 3: Whale Commands

  Command              Expected Output
  whale                ASCII whale art + "Whale Agent v1.0.0 -- Ready!"
  whale --version      "Whale Agent v1.0.0"
  whale --help         Usage info with 4 options
  whale --status       Status header with version/hostname/uptime
  whale --update       "Already up to date!"

## Test 4: One-Liner Install

  curl -sL https://YOUR_USERNAME.github.io/termux-whale-repo/install.sh | bash

## Troubleshooting

  Problem              Fix
  pkg update 404       Check GitHub Pages URL
  GPG errors           Add [trusted=yes] to sources.list
  Package not found    Wait for CI/CD to finish
