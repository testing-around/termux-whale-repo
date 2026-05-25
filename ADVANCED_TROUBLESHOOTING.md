# Advanced Troubleshooting Guide -- Termux Testing

Use this when TEST_PLAN.md steps fail and basic fixes aren't enough.

## 1. Common Package Installation Failures

### "Repository does not have a Release file"

  curl -s -o /dev/null -w "HTTP %{http_code}" https://USER.github.io/termux-whale-repo/dists/stable/Release
  # Expected: 200

  Fixes:
  - Wait 2-3 min for CI/CD to finish
  - Check URL spelling in sources.list
  - Ensure [trusted=yes] is present

### Hash Sum Mismatch

  pkg clean
  rm -rf $PREFIX/var/lib/apt/lists/*
  pkg update

### "Package whale-agent has no installation candidate"

  dpkg --print-architecture           # Check your arch
  curl -sL URL/dists/stable/Release | grep Architectures  # Check repo arches
  pkg list-all | grep whale           # List available packages

### Permission Denied

  chmod +x $PREFIX/bin/whale
  whale

## 2. Termux-Specific Quirks

  - Install Termux from F-Droid, NOT Google Play (Play is outdated)
  - $PREFIX = /data/data/com.termux/files/usr (not /usr)
  - Android 11+ storage: need termux-setup-storage

## 3. Network Troubleshooting

  # DNS check
  nslookup github.com

  # Test repo URL
  curl -I https://USER.github.io/termux-whale-repo/install.sh

  # Force IPv4
  echo 'Acquire::ForceIPv4 "true";' > $PREFIX/etc/apt/apt.conf.d/99force-ipv4

## 4. Quick Smoke-Test Script

  Save as smoke_test.sh on your Android device and run with: bash smoke_test.sh

  #!/data/data/com.termux/files/usr/bin/bash
  # Quick smoke test for WhaleTermux repo

  PASS=0
  FAIL=0

  test_pass() { PASS=$((PASS+1)); echo "  PASS: $1"; }
  test_fail() { FAIL=$((FAIL+1)); echo "  FAIL: $1"; }

  echo "=== WhaleTermux Smoke Test ==="

  # Test 1: Repo URL reachable
  echo "Test 1: Repo URL..."
  code=$(curl -s -o /dev/null -w "%{http_code}" https://USER.github.io/termux-whale-repo/dists/stable/Release 2>/dev/null)
  [ "$code" = "200" ] && test_pass "Release file reachable (HTTP $code)" || test_fail "Release file HTTP $code"

  # Test 2: Sources list exists
  echo "Test 2: Sources list..."
  [ -f $PREFIX/etc/apt/sources.list.d/whale.list ] && test_pass "whale.list exists" || test_fail "whale.list missing"

  # Test 3: Package installed
  echo "Test 3: Package..."
  which whale >/dev/null 2>&1 && test_pass "whale binary found" || test_fail "whale binary missing"

  # Test 4: whale --version
  echo "Test 4: whale --version..."
  whale --version >/dev/null 2>&1 && test_pass "whale --version works" || test_fail "whale --version failed"

  # Test 5: whale --help
  echo "Test 5: whale --help..."
  whale --help >/dev/null 2>&1 && test_pass "whale --help works" || test_fail "whale --help failed"

  # Summary
  echo ""
  echo "=== Results: $PASS passed, $FAIL failed ==="
  [ $FAIL -eq 0 ] && echo "All tests passed!" || echo "Some tests failed - check troubleshooting guide."
