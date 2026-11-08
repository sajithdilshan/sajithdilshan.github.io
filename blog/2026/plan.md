# FitMax — Implementation Plan

Personal iOS fitness tracker. Single user. Native SwiftUI, iCloud sync, Apple Health / Apple Watch integration, Liquid Glass design (iOS 26).

> **For the implementing agent:** Do not skip §3 (decisions) or §6 (CloudKit constraints). Build phase by phase (§11); each phase has acceptance criteria. Keep the app compiling and runnable after every phase.

> **Cost policy (MUST follow):** Use **Haiku** (`model: "haiku"`) subagents for executing commands and long-running tasks: `xcodegen generate`, `xcodebuild` builds and test runs, simulator boot/install/launch, `brew` installs, log and build-error triage, file searches, and repetitive mechanical edits. Spawn them with the Agent tool's `model: "haiku"` override, and have them return only a concise summary (pass/fail plus the relevant error lines with `file:line`). Reserve the main (larger) model for architecture decisions, writing non-trivial Swift code, and fixing errors the Haiku agent reports.

---

## 1. Product Summary

- **Home → Calendar tab:** month calendar. Each day shows markers for logged lifts, an Apple Watch workout, and progress photos. Tapping a day opens the **Day** screen.
- **Day screen:**
  - **Body weight**: read from Apple Health (the smart scale writes there). Manual entry is a fallback and writes to Health.
  - **Apple Watch workout(s)**: type, duration, active kcal, avg/max heart rate, and a heart-rate chart.
  - **Exercises**: name, then sets with reps and weight (kg) per set.
  - **Progress photos**: post-workout mirror selfies, one or more per day.
  - Notes.
- **Analytics tab:** per-exercise strength trends, volume, body-weight trend, workout frequency, and a side-by-side photo comparison.
- **Security:** iCloud private database (only the owner's Apple ID can access it) plus an optional Face ID app lock.
- **Out of scope for now:** data export, watchOS companion app, social/sharing, multi-user.

---

## 2. Target Platform & Tooling

| Item | Value |
|---|---|
| Xcode | 26.x (latest stable) |
| iOS deployment target | **iOS 26.1** (required for Liquid Glass APIs; the owner is the only user) |
| Language | Swift 6, strict concurrency **on** |
| UI | SwiftUI only (UIKit only where unavoidable: camera picker) |
| Persistence | SwiftData, with CloudKit sync to the private database |
| Charts | Swift Charts |
| Health | HealthKit (async query descriptors) |
| Auth lock | LocalAuthentication (Face ID) |
| Tests | Swift Testing (`import Testing`) for logic; Xcode Previews for UI |
| Third-party dependencies | **None.** Use only Apple frameworks. |
| Device | iPhone only (portrait primary; don't break landscape) |

---

## 3. Confirmed Decisions (from owner)

1. **Units: metric only.** Weight is kg (0.5 kg granularity for lifts, 0.1 kg for body weight). Use `Measurement<UnitMass>` for formatting, but store `Double` kg.
2. **Photos are progress photos** (how the owner looks after a workout), attached to a **day**, not to an exercise. Multiple per day are allowed. Exercises have no images.
3. **Body weight source of truth = Apple Health.** The smart scale writes there; the app reads `bodyMass`. Manual entry in the app **writes to Health** (so there's a single source of truth). The app does **not** store body weight in SwiftData.
4. **Apple Watch data** is read from HealthKit (`HKWorkout` plus heart rate and energy samples). The app does not write workouts in v1.
5. **Exercise library:** exercises are defined once (name, muscle group, tracking type) and reused when logging.
   - **Tracking types** (set on the exercise, locked once it has history): `weightReps` (kg × reps), `repsOnly` (30 burpees), `calories` (10 cal rowing), `distance` (150 m ski erg), `duration` (seconds, e.g. plank). Each set stores only the fields relevant to its type.
6. **Included nice-to-haves:** Face ID lock, "last time" hint, copy previous workout, private photos (never saved to the camera roll).
7. **Excluded:** export (CSV/JSON) for now.
8. **Design:** follow Apple's latest HIG with **Liquid Glass** (iOS 26). See §9.

---

## 4. Project Setup

### 4.1 Generate the project with XcodeGen (agent-friendly, reproducible)
The implementing agent works from the CLI, so the project is defined in `project.yml` rather than a hand-edited `.pbxproj`.

```bash
brew install xcodegen
cd ~/code/fitmax
git init                      # add .gitignore for Xcode (xcuserdata, DerivedData, *.xcodeproj is generated → ignore it)
xcodegen generate             # creates FitMax.xcodeproj from project.yml
```

`project.yml` essentials:
- Targets: `FitMax` (iOS app), `FitMaxTests` (unit tests, Swift Testing).
- `PRODUCT_BUNDLE_IDENTIFIER: com.example.fitmax` (placeholder; the owner replaces the prefix with their own).
- `DEVELOPMENT_TEAM`: empty until the owner sets it (Release configuration only).
- `SWIFT_VERSION: 6.0`, `SWIFT_STRICT_CONCURRENCY: complete`, `IPHONEOS_DEPLOYMENT_TARGET: 26.1`, `TARGETED_DEVICE_FAMILY: 1`.
- `CODE_SIGN_ENTITLEMENTS: FitMax/FitMax.entitlements`.
- Info.plist keys (see 4.3).
- Build configurations `Debug` / `Release`, plus a compile flag `ICLOUD_ENABLED` defined only in the Release configuration (see §6.3).

### 4.2 Entitlements (`FitMax.entitlements`)
| Key | Value |
|---|---|
| `com.apple.developer.healthkit` | `true` |
| `com.apple.developer.healthkit.access` | `[]` |
| `com.apple.developer.icloud-services` | `[CloudKit]` |
| `com.apple.developer.icloud-container-identifiers` | `[iCloud.com.example.fitmax]` |
| `aps-environment` | `development` (Xcode switches it for release) |

Background mode: `UIBackgroundModes = [remote-notification]` (CloudKit silent pushes for sync).

Keep two entitlements files: `FitMax.entitlements` (HealthKit only) and `FitMax-iCloud.entitlements` (HealthKit plus iCloud), selected per configuration. This keeps simulator builds free of iCloud capabilities.

### 4.3 Info.plist usage strings
- `NSHealthShareUsageDescription`: "FitMax reads your workouts, heart rate and body weight from Apple Health to show them alongside your training log."
- `NSHealthUpdateUsageDescription`: "FitMax saves body weight you enter manually to Apple Health."
- `NSCameraUsageDescription`: "FitMax uses the camera to take progress photos."
- `NSFaceIDUsageDescription`: "FitMax uses Face ID to keep your data private."
- Photo library: **not needed**. `PhotosPicker` runs out-of-process and needs no permission. Never write to the library.

### 4.4 Folder structure
```
FitMax/
  App/            FitMaxApp.swift, RootView.swift, AppLockGate.swift
  Models/         Exercise.swift, DayLog.swift, WorkoutEntry.swift, SetEntry.swift,
                  ProgressPhoto.swift, MuscleGroup.swift, DateKey.swift
  Persistence/    ModelContainerFactory.swift, DayLogRepository.swift, DuplicateMerger.swift,
                  PreviewData.swift
  Health/         HealthService.swift (actor), HealthModels.swift (WatchWorkoutSummary, BodyMassSample)
  Features/
    Calendar/     CalendarTab.swift, MonthGridView.swift, DayCell.swift
    Day/          DayView.swift, BodyWeightSection.swift, WatchWorkoutSection.swift,
                  ExercisesSection.swift, EntryEditorView.swift, SetRowView.swift,
                  PhotosSection.swift, PhotoViewer.swift, CopyPreviousWorkoutSheet.swift
    Exercises/    ExercisePickerSheet.swift, ExerciseLibraryView.swift, ExerciseFormView.swift
    Analytics/    AnalyticsTab.swift, ExerciseProgressChart.swift, VolumeChart.swift,
                  BodyWeightChart.swift, FrequencyChart.swift, PhotoCompareView.swift
    Settings/     SettingsView.swift
  Services/       ImageProcessor.swift, CameraPicker.swift, AppLock.swift, Analytics.swift (pure functions)
  Shared/         Formatters.swift, DesignTokens.swift, Components/ (GlassCard, StatTile, EmptyState)
  Resources/      Assets.xcassets (AppIcon, AccentColor)
FitMaxTests/      AnalyticsTests.swift, DateKeyTests.swift, DuplicateMergerTests.swift, ImageProcessorTests.swift
```

Architecture: plain SwiftUI with `@Query` and `@Environment(\.modelContext)` in views. Use `@Observable` view models only where logic is non-trivial (Analytics, Day's Health loading). Keep pure computation in `Analytics.swift` so it's testable. `HealthService` is an `actor` injected via `@Environment`.

---

## 5. Data Model (SwiftData, CloudKit-compatible)

All models live in one `Schema`, versioned with `VersionedSchema` (`FitMaxSchemaV1`) and a `SchemaMigrationPlan` from day one.

```swift
enum MuscleGroup: String, Codable, CaseIterable { case chest, back, shoulders, biceps, triceps, legs, glutes, core, fullBody, cardio, other }
enum TrackingType: String, Codable, CaseIterable { case weightReps, repsOnly, calories, distance, duration }

@Model final class Exercise {
    var id: UUID = UUID()
    var name: String = ""
    var muscleGroupRaw: String = MuscleGroup.other.rawValue
    var trackingTypeRaw: String = TrackingType.weightReps.rawValue  // weightReps | repsOnly | calories | distance | duration
    var createdAt: Date = Date.now
    var isArchived: Bool = false            // archive instead of delete when it has history
    @Relationship(deleteRule: .nullify, inverse: \WorkoutEntry.exercise)
    var entries: [WorkoutEntry]? = []
}

@Model final class DayLog {
    var id: UUID = UUID()
    var dateKey: String = ""                // "yyyy-MM-dd" in the user's current calendar. Logical primary key.
    var date: Date = Date.now               // startOfDay for dateKey, used for range queries/sorting
    var notes: String = ""
    var updatedAt: Date = Date.now
    @Relationship(deleteRule: .cascade, inverse: \WorkoutEntry.day)
    var entries: [WorkoutEntry]? = []
    @Relationship(deleteRule: .cascade, inverse: \ProgressPhoto.day)
    var photos: [ProgressPhoto]? = []
}

@Model final class WorkoutEntry {
    var id: UUID = UUID()
    var order: Int = 0
    var note: String = ""
    var createdAt: Date = Date.now
    var day: DayLog?
    var exercise: Exercise?
    @Relationship(deleteRule: .cascade, inverse: \SetEntry.entry)
    var sets: [SetEntry]? = []
}

@Model final class SetEntry {
    var id: UUID = UUID()
    var order: Int = 0
    var reps: Int = 0
    var weightKg: Double = 0               // 0 = bodyweight exercise
    var calories: Double = 0               // calories tracking
    var distanceM: Double = 0              // distance tracking, metres
    var durationSec: Int = 0               // duration tracking
    var entry: WorkoutEntry?
}

@Model final class ProgressPhoto {
    var id: UUID = UUID()
    var takenAt: Date = Date.now
    @Attribute(.externalStorage) var imageData: Data? = nil      // JPEG, ~2048px long edge → CKAsset
    @Attribute(.externalStorage) var thumbnailData: Data? = nil  // JPEG, ~400px long edge
    var day: DayLog?
}
```

**Not stored:** body weight and Watch workouts. They are always read live from HealthKit (Health syncs them via iCloud on its own).

### 5.1 DateKey rules (`DateKey.swift`)
- `DateKey.make(from: Date, calendar: .current) -> String`, and `DateKey.date(from: String) -> Date` (startOfDay).
- Always look up days by `dateKey`, never by `Date` equality. This avoids time-zone drift when traveling.
- Unit tests: DST boundaries, year boundary, and a time-zone change.

### 5.2 Fetch-or-create (`DayLogRepository`)
- `dayLog(for dateKey:) -> DayLog?` (fetch only) and `ensureDayLog(for dateKey:) -> DayLog` (create lazily, only when the user actually adds data). Don't create empty DayLogs just because a day was viewed.
- Delete a DayLog automatically when it becomes empty (no entries, no photos, empty notes).

## 6. iCloud Sync

### 6.1 CloudKit constraints (MUST follow, or sync silently fails)
- **No `@Attribute(.unique)`** anywhere.
- Every stored property has a **default value or is optional**.
- **All relationships are optional**, and every relationship has an inverse.
- No `.deny` delete rules.
- Schema changes after production deployment must be **additive only** (new optional fields/models). Never rename or delete fields; deprecate them instead.

### 6.2 Duplicate handling (`DuplicateMerger`)
Because uniqueness can't be enforced, two devices (or a race) may create two `DayLog`s with the same `dateKey`, or two `Exercise`s with the same name.
- Run on launch and whenever the app becomes active (debounced), and after remote change notifications (`NSPersistentStoreRemoteChange`).
- **DayLog:** group by `dateKey`. Keep the oldest `id`, move `entries` and `photos` to it, concatenate non-empty `notes`, then delete the rest.
- **Exercise:** group by case-insensitive trimmed `name`. Keep the oldest, re-point entries, delete the duplicates.
- Fully unit tested with an in-memory container.

### 6.3 Container configuration (`ModelContainerFactory`)
```swift
#if ICLOUD_ENABLED
let config = ModelConfiguration(schema: schema, cloudKitDatabase: .private("iCloud.com.example.fitmax"))
#else
let config = ModelConfiguration(schema: schema, cloudKitDatabase: .none)
#endif
```
- Previews and tests use `isStoredInMemoryOnly: true`.
- Settings screen shows the iCloud account status (`CKContainer.accountStatus()`): "Syncing with iCloud", "Signed out of iCloud", or "Local only (iCloud disabled in this build)".
- When migrating from the local-only build to the iCloud build, the existing local store must be preserved. Use the same store URL; SwiftData uploads existing records on first CloudKit-enabled launch. Verify this on device.

### 6.4 Production schema (do before relying on real data)
Builds run from Xcode use the CloudKit **Development** environment, which can be reset. Before real use:
1. Run the app once with iCloud enabled so the schema gets created in Development. Add one of every model type.
2. CloudKit Console (https://icloud.developer.apple.com) → container → **Deploy Schema Changes to Production**.
3. Install a **Release** build via TestFlight (which uses Production). See §12.

---

## 7. HealthKit Integration (`HealthService` actor)

### 7.1 Authorization
- Read: `HKObjectType.workoutType()`, `.quantityType(.heartRate)`, `.quantityType(.activeEnergyBurned)`, `.quantityType(.bodyMass)`.
- Write: `.quantityType(.bodyMass)` only.
- Ask on first launch via an onboarding card ("Connect Apple Health"), not automatically at app start. Use SwiftUI `.healthDataAccessRequest(store:shareTypes:readTypes:trigger:)`.
- HealthKit never reveals whether *read* access was denied. If queries return nothing, show a gentle hint: "No Health data. Check Settings → Health → Data Access → FitMax."
- Guard every call with `HKHealthStore.isHealthDataAvailable()`.

### 7.2 Queries (use `HKSampleQueryDescriptor` / `HKStatisticsQueryDescriptor` / `HKStatisticsCollectionQueryDescriptor`, async/await)
| Need | Query |
|---|---|
| Watch workouts for a day | `HKSampleQueryDescriptor` on workouts, predicate `startDate` within [startOfDay, startOfDay+1d), sorted by start |
| Workout summary | `workout.duration`, `workout.workoutActivityType`, `workout.statistics(for: activeEnergyBurned)?.sumQuantity()`, `workout.statistics(for: heartRate)` → average/max |
| Heart-rate chart | `HKSampleQueryDescriptor` on heartRate, predicate `HKQuery.predicateForObjects(from: workout)` (falls back to the workout's time window) |
| Body weight for a day | latest `bodyMass` sample within the day |
| Body-weight trend | `HKStatisticsCollectionQueryDescriptor`, `.discreteAverage`, daily interval, for the chosen range |
| Days with a Watch workout (calendar markers) | one workouts query for the visible month, mapped to `Set<String>` dateKeys |
| Manual weight entry | `HKQuantitySample(type: bodyMass, quantity: kg, start: now, end: now)` → `healthStore.save` |

- Expose `Sendable` value types (`WatchWorkoutSummary`, `HeartRatePoint`, `BodyMassPoint`) from the actor. Never pass `HKObject`s to views.
- Map `HKWorkoutActivityType` to a display name and SF Symbol (strength training → `figure.strengthtraining.traditional`, functional → `figure.strengthtraining.functional`, running → `figure.run`, HIIT → `figure.highintensity.intervaltraining`, default → `figure.mixed.cardio`).
- Show which device recorded the workout (`workout.sourceRevision.source.name`) as a caption.
- Cache per-month results in memory. Refresh on `scenePhase == .active` and pull-to-refresh. An `HKObserverQuery` isn't needed in v1.
- **Simulator:** the Health app in the simulator can add sample data manually. Also add a `#if DEBUG` "Seed Health sample data" button in Settings that writes fake body mass (and, if allowed, workouts) for UI testing.

---

## 8. Photos & Privacy

- **Capture:** `CameraPicker` (a `UIViewControllerRepresentable` around `UIImagePickerController`, `sourceType = .camera`, default **front** camera for selfies; the user can switch to rear). Also offer a `PhotosPicker` import (single or multiple).
- **Processing (`ImageProcessor`)**, done off the main actor:
  - Normalize orientation, downscale to a 2048px long edge, JPEG quality 0.8 (≈300–600 KB).
  - Thumbnail: 400px long edge, JPEG 0.7.
  - Strip metadata (GPS/EXIF) by re-encoding through `UIGraphicsImageRenderer` / ImageIO without properties.
- **Never save to the camera roll.** Images live only in SwiftData (and so in the iCloud private DB).
- Display thumbnails in grids. Load full images lazily in `PhotoViewer` (paged, pinch-to-zoom, delete with confirmation).
- **Privacy screen:** when `scenePhase != .active`, overlay a blurred/branded view so photos don't show in the app switcher.

### 8.1 App Lock (`AppLock` + `AppLockGate`)
- Setting "Require Face ID" (`@AppStorage`, default **on**).
- Lock when the app goes to the background, if more than 60 seconds have passed (configurable: Immediately / 1 min / 5 min).
- Unlock with `LAContext.evaluatePolicy(.deviceOwnerAuthentication)`, which falls back to the device passcode, so the owner can never get locked out.
- While locked: show a full-screen glass lock view with an "Unlock" button. App content must not render underneath (don't just overlay it; gate the view tree).

---

## 9. Design: Liquid Glass (iOS 26 HIG)

Reference: Apple HIG → "Materials" / "Liquid Glass", and the WWDC25 sessions "Meet Liquid Glass" and "Build a SwiftUI app with the new design".

### 9.1 Principles
- **Glass is for the navigation/control layer, not content.** Tab bar, toolbars, floating buttons, sheets and small controls get glass. Lists, cards of data, charts and photos sit underneath as content. Don't make every card glass.
- **Prefer system components.** They adopt Liquid Glass automatically when built with the iOS 26 SDK: `TabView` with the `Tab` API, `NavigationStack` toolbars, `.sheet`, `Menu`, `Picker`, `Slider`, `Toggle`. Don't add custom backgrounds behind toolbars or tab bars. Remove any `.toolbarBackground(...)` and `.presentationBackground(...)` overrides.
- **Don't stack glass on glass.** Group nearby custom glass elements in a `GlassEffectContainer` so they blend and morph correctly.
- Content should scroll **under** the bars (edge-to-edge). Use `.scrollEdgeEffectStyle(.soft, for: .top)` where appropriate.
- Support Light and Dark mode, Dynamic Type (up to the accessibility sizes in key screens), Reduce Transparency and Increase Contrast (the system handles glass fallbacks; verify custom glass elements remain legible), and VoiceOver labels on every icon-only button.
- Tint: one accent color (e.g. a vivid green/teal) defined in `AccentColor`. Use `.tint()` on prominent glass actions only.
- Typography: system fonts. Use `.largeTitle` navigation titles, and `.monospacedDigit()` for numbers in sets/stats.
- SF Symbols everywhere. Use `symbolEffect` subtly (e.g. bounce on adding a set).

### 9.2 APIs to use
| Where | API |
|---|---|
| Root tabs | `TabView { Tab("Calendar", systemImage: "calendar") {…}; Tab("Analytics", systemImage: "chart.xyaxis.line") {…}; Tab("Exercises", systemImage: "dumbbell") {…} }` plus `.tabBarMinimizeBehavior(.onScrollDown)` |
| "Today" quick access | `.tabViewBottomAccessory { TodayAccessoryView() }`: a compact glass pill ("Today · 3 exercises · 72.4 kg"); tapping it opens today's Day view |
| Primary actions | `.buttonStyle(.glassProminent)` (e.g. "Add Exercise", "Add Set"); secondary: `.buttonStyle(.glass)` |
| Custom floating controls | `.glassEffect(.regular.interactive(), in: .capsule)` inside a `GlassEffectContainer`; use `.glassEffectID(_:in:)` with a `@Namespace` for morphing transitions (e.g. calendar month switcher) |
| Toolbars | `ToolbarItem` / `ToolbarItemGroup`, and `ToolbarSpacer(.fixed)` to split groups into separate glass capsules |
| Sheets | Default sheet presentation (glass by default) with `.presentationDetents([.medium, .large])` |
| Photo headers | `.backgroundExtensionEffect()` on the latest progress photo hero, if one is used |

### 9.3 Screens

**A. Calendar tab** (`NavigationStack`, title = month name, e.g. "October 2026")
- Toolbar: `‹` `›` month navigation and a "Today" button (glass capsules, separate groups); a gear icon opens Settings as a sheet.
- `MonthGridView`: 7-column `LazyVGrid`; weekday header follows `Calendar.current.firstWeekday`. Supports horizontal swipe between months.
- `DayCell`: day number. Today is ringed with the accent; the selected day is filled. Up to three tiny markers below:
  - 🟢 lifts logged (`dumbbell.fill`, accent), ⌚️ Watch workout (`applewatch`, orange), 📷 photo (`camera.fill`, blue). Use small symbols or dots; VoiceOver reads "3 exercises, Apple Watch workout, 1 photo".
- Below the grid: a **day preview card** for the selected day (content, not glass): exercise names, set count, body weight, photo thumbnail. "Open Day" pushes `DayView`. Tapping a cell selects it; double-tap or tapping the card opens it.
- Data: `@Query` DayLogs in the visible month range (by `date`), plus Health workout dateKeys for the month.

**B. Day view** (pushed; title = "Mon, 26 Oct")
Scrollable sections (inset-grouped style or custom cards):
1. **Body weight**: big number "72.4 kg", with a change vs. the previous reading (▲/▼ 0.3 kg) and the source ("Withings" etc.). If none: "No weight today" and an "Add" button (sheet with a 0.1-step numeric field, saved to Health).
2. **Apple Watch**: one card per workout: symbol, type, start–end time, duration, active kcal, avg/max BPM, and a compact heart-rate `LineMark` chart with zone-colored `AreaMark`. Empty state: "No Apple Watch workout recorded".
3. **Exercises**: ordered list of `WorkoutEntry`. Each row shows the exercise name, sets inline ("10×60 · 10×60 · 8×62.5 kg") and a muted **"Last time: 3×10 @ 60 kg"** hint. Tapping opens `EntryEditorView`. Swipe to delete; use `onMove` to reorder (via an edit mode toolbar button).
   - Buttons: **Add Exercise** (glassProminent) and **Copy Previous Workout** (glass).
4. **Progress photos**: horizontal thumbnails, with a "+" menu offering "Take Photo" or "Choose from Library". Tapping a thumbnail opens `PhotoViewer`.
5. **Notes**: multiline `TextField(axis: .vertical)`.

**C. Exercise picker sheet** (`.presentationDetents([.medium, .large])`)
- `.searchable` list of non-archived exercises, grouped by muscle group and ordered by most recently used. "Create “<query>”" row when there's no match → inline form (name, muscle group and tracking type pickers).
- Selecting an exercise creates a `WorkoutEntry` **pre-filled with the sets from last time**, then opens the editor.

**D. Entry editor** (sheet or push)
- Header: exercise name and "Last time" summary (date plus sets).
- Set rows depend on the exercise's tracking type: `#` plus reps and kg (weightReps), reps only, calories, metres (10 m steps) or seconds, each a number field with a −/+ stepper (weight uses 0.5 steps), plus delete. Previous values, "Last time", copy-previous and day lists show the matching unit (`30 reps`, `10 cal`, `150 m`). Keep the keyboard numeric with a "Next" toolbar. Large touch targets (≥44pt), usable mid-workout.
- **Add Set** duplicates the last set's values.
- Live footer: total volume and est. 1RM of the best set (weightReps), or the total in the type's unit (other types).

**E. Copy previous workout sheet**
- Lists the most recent ~20 days with entries (date plus exercise names). Picking one appends those exercises, with their sets copied, to the current day.

**F. Exercises tab (library)**
- List grouped by muscle group with a usage count. Tap → detail: rename, change muscle group, mini progress chart, history list. Delete only if unused, otherwise **Archive**.

**G. Analytics tab** (see §10)

**H. Settings sheet**
- Face ID toggle plus lock delay; Apple Health connection status and a "Manage in Settings" link; iCloud status (§6.3); app version. `#if DEBUG`: seed sample data / wipe data.

---

## 10. Analytics

### 10.1 Calculations (`Analytics.swift`: pure, `Sendable`, unit-tested)
- **Non-weight exercises** (`repsOnly`, `calories`, `distance`, `duration`): the set's primary amount (reps / cal / m / sec) replaces weight. Session "Volume" = sum of amounts; "Top Set" and "e1RM" both mean best single set. Excluded from kg volume totals, the "Total volume" tile and volume-by-muscle-group. Chart units follow the type.
- **Set volume** = reps × weightKg. **Session volume** (per exercise per day) = Σ set volume.
- **Estimated 1RM (Epley)** = w × (1 + reps/30), for reps ≥ 1. If reps == 1, use w. Ignore sets with reps > 12 for e1RM (inaccurate); exclude weight 0.
- **Top set** per session = the max weightKg (ties broken by reps).
- **Personal records (PRs):** heaviest weight, best e1RM, and most volume in a session. Flag a session as a PR when it beats all previous sessions.
- **Workout frequency:** distinct days with ≥1 entry per ISO week (also count Watch-only workout days separately).
- **Body weight:** daily average from HealthKit, plus a 7-day moving average line.
- Time ranges: `1M, 3M, 6M, 1Y, All` (segmented `Picker`), shared across charts.

### 10.2 Analytics tab layout (scrolling; each block is a content card)
1. **Range picker** (top, segmented).
2. **Summary tiles** (2×2): workouts this range, total volume, current body weight (Δ over range), PRs this range.
3. **Exercise progress:** an exercise `Picker` (menu) and a metric picker (Top Set / e1RM / Volume). Swift Charts `LineMark` + `PointMark`, with PR points highlighted. Use `.chartXSelection` for scrubbing, showing date and value in an annotation.
4. **Body weight:** `LineMark` (daily) plus a smoothed 7-day average line, with the y-axis domain fitted to the data (not starting at 0).
5. **Weekly frequency:** `BarMark` per week (lifting days, plus stacked Watch-only days).
6. **Volume by muscle group:** `BarMark` horizontal, over the range.
7. **Photo compare:** pick two dates that have photos (defaults: earliest and latest in the range). Side-by-side view, plus a toggle for a **swipe slider overlay** (drag divider). Show the date and that day's body weight under each photo.

Empty states everywhere ("Log a few workouts to see trends") using `ContentUnavailableView`.

Performance: fetch the range's `WorkoutEntry`s once with a `FetchDescriptor` (predicate on `day.date`) and compute in a background `@ModelActor` or detached task mapped to value types. Don't compute inside `body`.

---

## 11. Implementation Phases

Each phase ends with: the project builds with no warnings under Swift 6 strict concurrency, tests pass, previews render, and the app runs in the simulator.

### Phase 1: Foundation
- XcodeGen project, entitlements variants, Info.plist strings, folder structure, `.gitignore`, `git init`.
- SwiftData models (§5), `VersionedSchema` V1, `ModelContainerFactory` (local-only by default), `DateKey`, `DayLogRepository`, `DuplicateMerger`, `PreviewData` (in-memory sample: 10 exercises, ~8 weeks of logs).
- Root `TabView` with three placeholder tabs and a Settings sheet.
- Tests: DateKey, DuplicateMerger, repository fetch-or-create and empty-day cleanup.
- ✅ Accept: app launches to tabs; sample data shows in previews; tests are green.

### Phase 2: Calendar and Day logging
- Calendar tab (§9.3 A) with lift and photo markers (Watch markers come in Phase 4).
- Day view with Exercises and Notes sections; exercise picker; entry editor; "last time" hint; copy previous workout; Exercises library tab.
- ✅ Accept: on device, log 3 exercises with sets in under 60s; data persists across relaunch; deleting the last entry removes the empty DayLog.

### Phase 3: Progress photos and privacy
- `CameraPicker`, `PhotosPicker`, `ImageProcessor`, photos section, `PhotoViewer`.
- App-switcher privacy overlay, `AppLock` / `AppLockGate` with Face ID, and Settings toggles.
- Tests: `ImageProcessor` output size/dimensions and metadata stripping.
- ✅ Accept: photo taken on device appears in the day; not in Camera Roll; no GPS EXIF; lock screen appears after backgrounding past the delay.

### Phase 4: Apple Health and Apple Watch
- `HealthService` (§7), onboarding connect card, body-weight section (read plus manual write), Watch workout cards with HR chart, calendar ⌚️ markers, Today bottom accessory.
- ✅ Accept: in the Simulator with seeded Health data now; on the real iPhone (via TestFlight, after Phase 6): yesterday's Watch strength workout shows with correct duration, kcal and HR; the scale weight shows; a manual weight appears in the Health app.

### Phase 5: Analytics
- `Analytics.swift` and its tests (Epley, volume, PR detection, weekly frequency, moving average), then the Analytics tab (§10.2) including photo compare.
- ✅ Accept: charts match hand-calculated values for the preview data set; scrubbing works; empty states render.

### Phase 6: iCloud sync and Xcode Cloud

**Steps:**

1. **Team ID (agent):** the owner provides the 10-character Team ID. The agent sets `DEVELOPMENT_TEAM` in the **Release** config only (Debug and simulator stay unsigned), regenerates the project, builds Debug and Release for the simulator, and pushes.
2. **App ID (owner, browser):** developer.apple.com → Certificates, Identifiers & Profiles → Identifiers → **+** → App IDs → App. Bundle ID (explicit) `com.example.fitmax`. Enable **HealthKit** and **iCloud** (include CloudKit support). Do this on the web, not in Xcode.
3. **iCloud container (owner, browser):** Identifiers → **+** → iCloud Containers → ID `iCloud.com.example.fitmax`. Then open the App ID, edit iCloud → Configure, and attach this container.
4. **App Store Connect record (owner, browser):** appstoreconnect.apple.com → Apps → **+** → New App. Platform iOS, name "FitMax", primary language, bundle ID `com.example.fitmax`, any SKU (e.g. `fitmax-1`).
5. **Xcode Cloud workflow (owner):** create it from App Store Connect → the app → Xcode Cloud, or from Xcode if the web flow isn't available.
   - Connect the GitHub repo `<user>/fitmax` (private) and grant the Xcode Cloud GitHub app access to it.
   - The repo has no committed `.xcodeproj`. Add a **post-clone script** `ci_scripts/ci_post_clone.sh` that installs XcodeGen and runs `xcodegen generate` (agent writes and commits it).
   - Workflow: start condition = push to `main`; environment = latest Xcode; action = **Archive** (scheme `FitMax`, Release, iOS); post-action = **TestFlight Internal Testing**.
6. **First build (owner + agent):** push to `main` (or start the workflow manually). Fix any archive or signing errors the workflow reports (agent triages the logs). Wait for the build to appear in App Store Connect → TestFlight.
7. **TestFlight (owner):** add yourself as an **Internal Tester** (App Store Connect → Users and Access → your Apple ID has the role; TestFlight → Internal Testing → add group). Install the **TestFlight** app on the iPhone, accept the invite, and install FitMax.
8. **Run the app once with iCloud on (owner, device):** sign in to iCloud on the phone, open FitMax, grant Health access, and add one of every record type (a day with an exercise and sets, a note, a progress photo, an exercise of each tracking type). This creates the CloudKit schema in the **Development** environment.
9. **Deploy the schema to Production (owner, browser):** CloudKit Console (icloud.developer.apple.com) → container `iCloud.com.example.fitmax` → Schema → **Deploy Schema Changes to Production**. TestFlight builds use the Production environment, so do this before relying on real data (§6.4).
10. **Verify sync (owner, device):** confirm Settings shows "iCloud sync: On"; log a workout, delete the app, reinstall from TestFlight, and confirm all logs and photos come back. If a second device is available, confirm changes sync both ways and the duplicate merger leaves one day per date.
11. **Verify the data migration:** if any data was created in a local-only build earlier, check that it uploaded on the first iCloud-enabled launch (same store URL, §6.3).
12. **Ongoing:** TestFlight builds expire after 90 days. Push a new build to `main` at least every ~80 days. Only additive schema changes after the Production deploy (§6.1).

- ✅ Accept: reinstall restores all logs and photos; Settings shows iCloud sync On; a manual weight entry appears in the Health app.

### Phase 7: Design polish and accessibility
- Liquid Glass audit against §9 (no custom bar backgrounds, `GlassEffectContainer` grouping, morph transitions), Dark Mode, Dynamic Type XXL, VoiceOver pass, Reduce Transparency/Motion, haptics (`.sensoryFeedback`) on add set / PR, app icon (with iOS 26 layered icon via Icon Composer if available).
- ✅ Accept: Accessibility Inspector audit has no critical issues.

---

## 12. Installing on the Owner's iPhone

- **During development:** iOS Simulator only. Do not connect the iPhone for Xcode device builds.
- **On device:** App Store Connect → My Apps → "+" New App (bundle ID from §4.1, name "FitMax"). Builds come from **Xcode Cloud → TestFlight Internal**, never from a local Archive on the development Mac. Install via the TestFlight app.
  - TestFlight builds **expire after 90 days**, so upload a new build at least every ~80 days. No App Store review is needed for internal testing. Data is unaffected by build expiry/reinstall because it lives in iCloud.
- Never submit to the public App Store (not needed).

---

## 13. Future (not in v1)
- watchOS companion app for logging sets on the wrist and starting an `HKWorkoutSession`.
- Data export (CSV/JSON) and import.
- Workout templates/routines, rest timer with Live Activity.
- Widgets (streak, last weigh-in), Siri/App Intents ("Log 10 reps at 60 kg").
