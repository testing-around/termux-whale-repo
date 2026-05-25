# GPG Signing Guide -- WhaleTermux APT Repository

> Current: [trusted=yes] (unsigned). Goal: GPG-signed Release file.

## 1. Generate a GPG Signing Key

  gpg --full-generate-key

  Option              Choice
  Key type            RSA and RSA (option 1)
  Key size            4096
  Expiration          0 = does not expire
  Real name           WhaleTermux Repository
  Email               whale@example.com

  Get your Key ID:  gpg --list-keys --keyid-format LONG

## 2. Export the Public Key

  gpg --armor --export KEY_ID > public_key.asc
  gpg --export KEY_ID > public_key.gpg
  # Place public_key.gpg in termux-repo/repo/

## 3. Sign the Release File

  cd termux-repo/repo/dists/stable/
  gpg --detach-sign --armor -o Release.gpg Release
  gpg --clearsign -o InRelease Release

  # Verify:  gpg --verify Release.gpg Release

## 4. Update install.sh (remove [trusted=yes], add key import)

  BEFORE:  echo "deb [trusted=yes] https://... stable main"
  AFTER:   curl -sL URL/public_key.gpg > $PREFIX/etc/apt/trusted.gpg.d/whale.gpg
           echo "deb https://... stable main" (no trusted flag)

## 5. Update CI/CD (add signing step to deploy.yml)

  Add a step after 'Generate APT repo' to:
  - Import the GPG private key (from GitHub Secrets)
  - Run gpg --detach-sign and gpg --clearsign
  - Copy public_key.gpg into the repo directory
