# CLI Reference

Detailed command reference for iOS build and simulator management.

## xcodebuild

### Project Discovery

```bash
# List schemes, targets, and build configurations
xcodebuild -list

# For workspace
xcodebuild -workspace App.xcworkspace -list

# Show available SDKs
xcodebuild -showsdks

# Show available destinations for a scheme
xcodebuild -workspace App.xcworkspace -scheme App -showdestinations

# Print build settings
xcodebuild -workspace App.xcworkspace -scheme App -showBuildSettings
```

### Building

```bash
# Basic build for simulator
xcodebuild -workspace App.xcworkspace \
  -scheme App \
  -destination "platform=iOS Simulator,name=iPhone 16 Pro" \
  build

# Build with specific simulator UDID
xcodebuild -workspace App.xcworkspace \
  -scheme App \
  -destination "platform=iOS Simulator,id=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX" \
  build

# Custom derived data path (for finding .app bundle)
xcodebuild -workspace App.xcworkspace \
  -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  -derivedDataPath ./DerivedData \
  build

# Build for device (generic)
xcodebuild -workspace App.xcworkspace \
  -scheme App \
  -destination "generic/platform=iOS" \
  build
```

**Key Flags:**

| Flag | Description |
|------|-------------|
| `-workspace` | Path to `.xcworkspace` file |
| `-project` | Path to `.xcodeproj` file (if no workspace) |
| `-scheme` | Build scheme name |
| `-destination` | Target device/simulator |
| `-derivedDataPath` | Custom build output directory |
| `-configuration` | Debug or Release |
| `-sdk` | Target SDK (iphoneos, iphonesimulator) |

### Testing

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

# Run specific test method
xcodebuild test \
  -workspace App.xcworkspace \
  -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  -only-testing:AppTests/LoginTests/testValidLogin

# Skip specific tests
xcodebuild test \
  -workspace App.xcworkspace \
  -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  -skip-testing:AppTests/SlowTests

# Enable code coverage
xcodebuild test \
  -workspace App.xcworkspace \
  -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  -enableCodeCoverage YES
```

### Archiving

```bash
# Create archive
xcodebuild archive \
  -workspace App.xcworkspace \
  -scheme App \
  -archivePath ./build/App.xcarchive

# Export IPA
xcodebuild -exportArchive \
  -archivePath ./build/App.xcarchive \
  -exportPath ./build \
  -exportOptionsPlist ExportOptions.plist
```

## xcrun simctl

### Device Management

```bash
# List all devices
xcrun simctl list devices

# List available devices only
xcrun simctl list devices available

# List as JSON (for parsing)
xcrun simctl list devices --json

# List booted devices
xcrun simctl list devices booted

# Boot simulator
xcrun simctl boot $UDID

# Shutdown simulator
xcrun simctl shutdown $UDID

# Shutdown all simulators
xcrun simctl shutdown all

# Erase simulator (factory reset)
xcrun simctl erase $UDID

# Create new simulator
xcrun simctl create "My iPhone" "iPhone 16 Pro" "iOS18.0"

# Delete simulator
xcrun simctl delete $UDID
```

### Finding Simulator UDIDs

```bash
# Get first booted simulator
xcrun simctl list devices booted --json | jq -r '.devices[][] | select(.state == "Booted") | .udid' | head -1

# Find iPhone 16 Pro
xcrun simctl list devices available --json | jq -r '.devices[][] | select(.name == "iPhone 16 Pro") | .udid' | head -1

# Find any available iPhone
xcrun simctl list devices available --json | jq -r '.devices[][] | select(.name | contains("iPhone")) | .udid' | head -1
```

### App Operations

```bash
# Install app
xcrun simctl install $UDID path/to/App.app

# Launch app
xcrun simctl launch $UDID com.example.app

# Launch with console output (stdout/stderr)
xcrun simctl launch --console $UDID com.example.app

# Launch with arguments
xcrun simctl launch $UDID com.example.app --arg1 value1

# Terminate app
xcrun simctl terminate $UDID com.example.app

# Uninstall app
xcrun simctl uninstall $UDID com.example.app

# Get app container path
xcrun simctl get_app_container $UDID com.example.app
xcrun simctl get_app_container $UDID com.example.app data  # Data container
```

### Screen Capture

```bash
# Screenshot
xcrun simctl io $UDID screenshot screenshot.png

# Screenshot to stdout (for piping)
xcrun simctl io $UDID screenshot -

# Record video
xcrun simctl io $UDID recordVideo output.mp4

# Record in background
xcrun simctl io $UDID recordVideo output.mp4 &
RECORD_PID=$!

# Stop recording (must use SIGINT for proper file finalization)
kill -2 $RECORD_PID
```

### Environment Simulation

```bash
# Set location
xcrun simctl location $UDID set 37.7749,-122.4194

# Clear location
xcrun simctl location $UDID clear

# Override status bar
xcrun simctl status_bar $UDID override \
  --time "9:41" \
  --batteryState charged \
  --batteryLevel 100 \
  --cellularMode active \
  --cellularBars 4

# Clear status bar override
xcrun simctl status_bar $UDID clear

# Send push notification
xcrun simctl push $UDID com.example.app payload.json

# Grant privacy permissions
xcrun simctl privacy $UDID grant photos com.example.app
xcrun simctl privacy $UDID grant camera com.example.app
xcrun simctl privacy $UDID grant microphone com.example.app
xcrun simctl privacy $UDID grant location com.example.app
```

### Deep Links & URLs

```bash
# Open URL (deep link)
xcrun simctl openurl $UDID "myapp://path/to/screen"

# Open web URL in Safari
xcrun simctl openurl $UDID "https://example.com"
```

### Pasteboard

```bash
# Get pasteboard contents
xcrun simctl pbpaste $UDID

# Set pasteboard contents
xcrun simctl pbcopy $UDID "text to copy"
```

## Tuist Commands

For projects using Tuist with mise:

```bash
# Install dependencies (SPM, etc.)
mise exec -- tuist install

# Generate Xcode project
mise exec -- tuist generate

# Clean generated files
mise exec -- tuist clean

# Edit project manifest
mise exec -- tuist edit
```

## Complete Workflow Script

```bash
#!/bin/bash
set -e

# Find or boot simulator
UDID=$(xcrun simctl list devices available --json | jq -r '.devices[][] | select(.name == "iPhone 16 Pro") | .udid' | head -1)

if [ -z "$UDID" ]; then
  echo "No iPhone 16 Pro simulator found"
  exit 1
fi

# Check if booted
STATE=$(xcrun simctl list devices --json | jq -r ".devices[][] | select(.udid == \"$UDID\") | .state")
if [ "$STATE" != "Booted" ]; then
  echo "Booting simulator..."
  xcrun simctl boot $UDID
fi

# Build
echo "Building..."
xcodebuild -workspace App.xcworkspace \
  -scheme App \
  -destination "platform=iOS Simulator,id=$UDID" \
  -derivedDataPath ./DerivedData \
  build

# Find app bundle
APP_PATH=$(find ./DerivedData -name "*.app" -type d | head -1)
BUNDLE_ID=$(defaults read "$APP_PATH/Info.plist" CFBundleIdentifier)

# Install and launch
echo "Installing and launching..."
xcrun simctl install $UDID "$APP_PATH"
xcrun simctl launch --console $UDID $BUNDLE_ID
```

## Troubleshooting

### Common Errors

**"xcodebuild: error: The project 'X' does not contain a scheme named 'Y'"**
- Run `xcodebuild -list` to see available schemes
- Check if workspace vs project flag is needed

**"Unable to find a destination matching the provided destination specifier"**
- Run `xcrun simctl list devices available` to see valid simulators
- Check iOS version compatibility with your project

**"The request was denied by service delegate"**
- Simulator may need to be booted first
- Try `xcrun simctl boot $UDID`

**Recording produces empty/corrupted file**
- Must stop with `kill -2` (SIGINT), not `kill -9`
- Recording process needs graceful termination to write file headers

### Performance Tips

- Use `-derivedDataPath` to avoid rebuilding from scratch
- Use `-destination` with UDID instead of name for faster matching
- Shutdown unused simulators to free memory
