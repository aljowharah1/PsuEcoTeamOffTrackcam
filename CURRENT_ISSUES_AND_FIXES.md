# 🔧 Current Issues & Fixes

## ✅ WORKING
- Camera stream to dashboard
- Dashboard UI loads
- Racing line data (using local fallback)
- MQTT connected initially

## ❌ ISSUES TO FIX

### 1. GPS Data All Zeros (Priority: HIGH)
**Problem**: GPS showing `0.000000 0.000000` repeatedly

**Possible Causes**:
- GPS module not getting satellite fix (indoors?)
- GPS antenna not connected
- GPS module not configured correctly

**Quick Test**:
```bash
# On Pi, check raw GPS output
cat /dev/serial0
```

Should see NMEA sentences like:
```
$GPGGA,123456.00,2548.8435,N,05145.0190,E,1,08,0.9,23.4,M...
```

If you see nothing or garbled data, GPS is not working.

**Fix**:
1. Make sure GPS module is outdoors with clear sky view
2. Wait 2-5 minutes for GPS fix (cold start)
3. Check GPS antenna connection
4. Verify `/dev/serial0` is correct GPS port

---

### 2. CORS Error - Racing Line API (Priority: MEDIUM)
**Problem**: API call to Vercel blocked by CORS

**Current Status**:
- API code has CORS headers (lines 283, 299, 313-315)
- But not deployed to Vercel yet OR Vercel needs rebuild

**Fix**:
Redeploy to Vercel:
```bash
# If you have Vercel CLI installed
cd C:\Users\Juju\Desktop\PSU_ECOteam_offtrack_award
vercel --prod
```

OR use Vercel dashboard to trigger new deployment.

**Workaround**:
The app already falls back to local racing line data, so overlay should still work without the API!

---

### 3. MQTT Goes Offline (Priority: MEDIUM)
**Problem**: `📡 MQTT offline - switching to GPS fallback mode`

**Possible Causes**:
- HiveMQ Cloud credentials expired
- Network issue (Pi can't reach internet)
- MQTT broker down

**Test MQTT**:
```bash
# On Pi, test MQTT connection
pip3 install paho-mqtt
python3 << EOF
import paho.mqtt.client as mqtt
client = mqtt.Client()
client.username_pw_set("ShellJM", "psuEcoteam1st")
client.tls_set()
client.connect("8fac0c92ea0a49b8b56f39536ba2fd78.s1.eu.hivemq.cloud", 8883, 60)
print("MQTT Connected!")
EOF
```

If this fails, MQTT credentials or broker might be the issue.

**Impact**:
- Can't receive telemetry from car (current, voltage, power)
- GPS fallback mode activates (uses phone GPS instead)

---

### 4. Browser GPS Requires HTTPS (Priority: LOW)
**Problem**: `GPS Error: Only secure origins are allowed`

**Cause**:
Modern browsers require HTTPS to access device GPS API for security.

**Options**:
A. **Use Pi GPS instead** (preferred - that's what we built!)
B. Access via `localhost` (works on same device only)
C. Set up HTTPS on Pi (complex, need certificate)

**Current Workaround**:
The app is designed to use **Pi GPS**, not phone GPS. So this error is expected and okay! The MQTT offline fallback to phone GPS won't work over HTTP, but that's fine - we want Pi GPS anyway.

---

## 🎯 ACTION PLAN

### Immediate (Test Today):

1. **Test GPS Module**:
   ```bash
   ssh pi@berryspie
   cat /dev/serial0
   ```
   - Go outdoors, wait for GPS fix
   - Should see NMEA sentences with valid coordinates

2. **Test with Old File** (your request):
   - Do you have an old telemetry data file we can replay?
   - Or simulate with fake GPS data?

3. **Check Racing Line Overlay**:
   - Even with GPS at 0,0, overlay should appear (will just be off-track)
   - Check if green line is visible on camera

### Next Steps:

4. **Fix GPS** if module test fails
5. **Redeploy Vercel API** for proper CORS (optional - fallback works)
6. **Test MQTT** connection to fix telemetry
7. **Add mDNS** for hostname access

---

## 📝 TESTING CHECKLIST

### Test Current Interface:

- [ ] Dashboard loads
- [ ] Camera stream visible
- [ ] Map shows (even with wrong GPS)
- [ ] Speed/Current/Voltage displays (will be 0 without MQTT)
- [ ] Lap timer exists
- [ ] Racing line overlay visible on camera

### Test with Simulated Data:

If GPS not working, we can:
1. Hardcode test GPS coordinates in script
2. Replay old telemetry log file
3. Publish test MQTT messages

Want me to create a test data simulator?

---

## 🔍 WHY GPS IS PROBABLY THE MAIN ISSUE

Looking at your logs:
- GPS consistently returns `0.000000 0.000000` (no fix)
- This causes wrong map position
- This causes racing line overlay to be off
- This causes MQTT to go offline (maybe needs valid GPS?)

**Once GPS works, most issues should resolve!**

---

## 💡 QUICK TEST WITHOUT GPS

Want to see the overlay working? We can temporarily hardcode Lusail coordinates:

```javascript
// In script.js, replace GPS data with test coordinates
const testGPS = {
    latitude: 25.488435,
    longitude: 51.450190,
    speed: 25,
    heading: 45
};
```

This will show the racing line overlay as if you're on track!

---

## 🏁 SUMMARY

**Priority Order**:
1. Fix GPS (outdoor test, check module)
2. Test interface with old data file OR simulated data
3. Fix MQTT connection
4. Redeploy Vercel API (optional)

**What's Already Working**:
- Camera stream ✅
- Dashboard UI ✅
- Auto-start ✅
- Resource cleanup ✅
- Local racing line fallback ✅

You're 80% there! Just need to get GPS signal and verify overlay rendering.
