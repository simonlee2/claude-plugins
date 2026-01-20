---
name: ios-build-test
description: Use when user asks to "build iOS app", "run on simulator", "test iOS", "record simulator video", "reset app", "reset onboarding", or needs Xcode builds and simulator management.
---

# iOS Build & Test Skill

Build and manage iOS apps using native Xcode CLI tools (`xcodebuild`, `xcrun simctl`).

## When to Use

- Building iOS/macOS apps with Xcode
- Running apps in iOS simulators
- Managing simulator instances (boot, shutdown, list)
- Taking screenshots or recording video
- Running unit/UI tests
- Resetting app state or onboarding flows

## Build Workflow

### 1. Discover Project Structure

```bash
# List available schemes
xcodebuild -list

# For workspaces
xcodebuild -workspace App.xcworkspace -list
```

### 2. Find Available Simulators

```bash
# List all devices
xcrun simctl list devices

# Get booted simulator UDID
xcrun simctl list devices booted --json | jq -r '.devices[][] | select(.state == "Booted") | .udid'

# Find specific device type
xcrun simctl list devices available --json | jq -r '.devices[][] | select(.name | contains("iPhone 16")) | .udid' | head -1
```

### 3. Boot Simulator (if needed)

```bash
xcrun simctl boot $UDID
```

### 4. Build for Simulator

```bash
xcodebuild -workspace App.xcworkspace \
  -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  -derivedDataPath ./DerivedData \
  build
```

### 5. Install and Launch

```bash
# Find .app bundle
APP_PATH=$(find ./DerivedData -name "*.app" -type d | head -1)

# Install
xcrun simctl install $UDID "$APP_PATH"

# Launch (get bundle ID from Info.plist)
BUNDLE_ID=$(defaults read "$APP_PATH/Info.plist" CFBundleIdentifier)
xcrun simctl launch $UDID $BUNDLE_ID

# Launch with console output
xcrun simctl launch --console $UDID $BUNDLE_ID
```

## Reset App State

Useful for testing onboarding flows or clean state:

```bash
# Uninstall app
xcrun simctl uninstall $UDID $BUNDLE_ID

# Reinstall and launch
xcrun simctl install $UDID "$APP_PATH"
xcrun simctl launch $UDID $BUNDLE_ID
```

To fully reset simulator:

```bash
xcrun simctl erase $UDID
```

## Video Capture

Record simulator screen:

```bash
# Start recording in background
xcrun simctl io $UDID recordVideo output.mp4 &
RECORD_PID=$!

# ... perform actions ...

# Stop recording (SIGINT)
kill -2 $RECORD_PID
```

Screenshot:

```bash
xcrun simctl io $UDID screenshot screenshot.png
```

## Running Tests

```bash
# Run all tests
xcodebuild test \
  -workspace App.xcworkspace \
  -scheme App \
  -destination "platform=iOS Simulator,id=$UDID"

# Run specific test class
xcodebuild test \
  -workspace App.xcworkspace \
  -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  -only-testing:AppTests/LoginTests

# With code coverage
xcodebuild test \
  -workspace App.xcworkspace \
  -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  -enableCodeCoverage YES
```

## Tuist Projects

For projects using Tuist:

```bash
# Install dependencies and generate Xcode project
mise exec -- tuist install
mise exec -- tuist generate

# Then use standard xcodebuild commands
```

## XcodeBuildMCP Integration

If XcodeBuildMCP tools are available, prefer those for:
- Project discovery
- Build operations
- Simulator management

Fall back to CLI commands when MCP isn't available or for operations not covered by MCP tools.

## Quick Reference

| Task | Command |
|------|---------|
| List schemes | `xcodebuild -list` |
| List simulators | `xcrun simctl list devices` |
| Boot simulator | `xcrun simctl boot $UDID` |
| Build | `xcodebuild -workspace X -scheme Y -destination "..." build` |
| Install app | `xcrun simctl install $UDID path/to/App.app` |
| Launch app | `xcrun simctl launch $UDID com.bundle.id` |
| Uninstall | `xcrun simctl uninstall $UDID com.bundle.id` |
| Screenshot | `xcrun simctl io $UDID screenshot file.png` |
| Record video | `xcrun simctl io $UDID recordVideo file.mp4` |
| Run tests | `xcodebuild test -workspace X -scheme Y -destination "..."` |

## Common Issues

**Build fails with "no scheme"**: Use `-list` to find available schemes, specify with `-scheme`.

**Simulator not found**: Ensure UDID is correct. Use `xcrun simctl list devices available` to find valid simulators.

**App won't launch**: Check bundle ID matches what's in Info.plist. Use `--console` flag to see launch errors.

**Video recording won't stop**: Use `kill -2` (SIGINT), not `kill -9`. The recording needs graceful termination to finalize the file.

See `CLI_REFERENCE.md` for complete command documentation.
