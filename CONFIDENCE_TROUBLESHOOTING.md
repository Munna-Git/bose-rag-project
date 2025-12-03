# 🔍 Confidence Score Troubleshooting

## Step-by-Step Debugging

### Step 1: Verify Configuration
```powershell
# Check .env file has confidence enabled
Get-Content .env | Select-String "CONFIDENCE"
```

**Expected output:**
```
ENABLE_CONFIDENCE_SCORING=true
```

---

### Step 2: Restart System (CRITICAL!)
```powershell
# Stop current server (Ctrl+C)
# Then restart:
python app.py
```

**Look for in startup logs:**
```
SUCCESS: Confidence scorer initialized
Enhancements enabled: Hybrid Search, Query Cache, Confidence Scoring, Metrics
```

If you see "Confidence scoring disabled", the .env isn't being read properly.

---

### Step 3: Test Confidence API Directly
Open browser and visit:
```
http://localhost:8000/api/test-confidence
```

**Expected response:**
```json
{
  "confidence_scoring_enabled": true,
  "test_confidence": {
    "overall": 0.87,
    "label": "high",
    "breakdown": {...},
    "explanation": "High confidence. Answer is based...",
    "enabled": true
  },
  "message": "Confidence scoring is working!"
}
```

**If you see `"confidence_scoring_enabled": false`:**
- Your .env file isn't being loaded
- Try setting environment variable directly in PowerShell before starting:
  ```powershell
  $env:ENABLE_CONFIDENCE_SCORING="true"
  python app.py
  ```

---

### Step 4: Check Browser Console
1. Open DevTools (F12)
2. Go to Console tab
3. Ask a question in the UI
4. Look for these log messages:

**What you should see:**
```javascript
Query response: {
  status: "success",
  confidence: {
    overall: 0.87,
    label: "high",
    enabled: true,
    ...
  },
  ...
}

Checking confidence data: {overall: 0.87, label: "high", ...}
✓ Adding confidence indicator: {overall: 0.87, label: "high", ...}
```

**What indicates a problem:**
```javascript
// Problem 1: No confidence field at all
Query response: {status: "success", answer: "...", sources: [...]}
// Solution: Check logs, confidence might not be calculating

// Problem 2: Confidence is null
Checking confidence data: null
ℹ No confidence data in response
// Solution: Check API test endpoint

// Problem 3: Confidence missing overall
✗ Confidence data present but invalid format: {enabled: false}
// Solution: Confidence is disabled, check .env
```

---

### Step 5: Check Backend Logs
Look at the console where you ran `python app.py`:

**Successful confidence calculation:**
```
Calculating confidence score...
Confidence calculated: {'overall': 0.87, 'label': 'high', ...}
Adding confidence to result: {'overall': 0.87, ...}
```

**Problem indicators:**
```
WARNING: No confidence score to add to result
// Means confidence calculation returned None

Confidence scoring disabled in config
// Means ENABLE_CONFIDENCE_SCORING=false in settings
```

---

### Step 6: Manual Test Query
Run this in PowerShell:

```powershell
$body = @{
    question = "What is the frequency response?"
    verbose = $false
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $body -ContentType "application/json"

# Check if confidence exists
if ($response.confidence) {
    Write-Host "✓ Confidence found:" $response.confidence.overall $response.confidence.label -ForegroundColor Green
} else {
    Write-Host "✗ No confidence in response" -ForegroundColor Red
}

# Show full response
$response | ConvertTo-Json -Depth 10
```

---

### Step 7: Force Fresh Start
If nothing works, try a complete reset:

```powershell
# 1. Stop server
# 2. Clear Python cache
Remove-Item -Recurse -Force .\**\__pycache__

# 3. Verify .env
Get-Content .env

# 4. Set environment variable manually
$env:ENABLE_CONFIDENCE_SCORING="true"

# 5. Start with verbose output
python app.py
```

---

## Common Issues & Solutions

### Issue 1: "Confidence scoring disabled in config"
**Cause:** .env file not loaded or variable set to false

**Solutions:**
1. Check .env has `ENABLE_CONFIDENCE_SCORING=true` (no quotes, no spaces)
2. Restart the system
3. Set environment variable manually before starting:
   ```powershell
   $env:ENABLE_CONFIDENCE_SCORING="true"
   python app.py
   ```

### Issue 2: Confidence in API but not in UI
**Cause:** Frontend not rendering the badge

**Check:**
1. Browser console shows confidence data
2. But no badge appears
3. Check CSS is loaded (styles.css)

**Solution:**
- Hard refresh browser (Ctrl+Shift+R)
- Clear browser cache
- Check for JavaScript errors in console

### Issue 3: Works for first query, not for cached
**Cause:** Cache stores old responses without confidence

**Solution:**
```powershell
# Clear cache via API
Invoke-RestMethod -Uri "http://localhost:8000/api/cache/clear" -Method Post
```

### Issue 4: "enabled": false in response
**Cause:** Confidence scoring actually disabled

**Check:**
```powershell
# Visit this URL
http://localhost:8000/api/test-confidence
```

If it says `"confidence_scoring_enabled": false`, your config isn't loading.

---

## Quick Verification Checklist

- [ ] .env file has `ENABLE_CONFIDENCE_SCORING=true`
- [ ] System restarted after .env change
- [ ] Startup logs show "Confidence Scoring" in enhancements
- [ ] `/api/test-confidence` returns enabled=true
- [ ] Browser console shows confidence in query response
- [ ] Browser console shows "✓ Adding confidence indicator"
- [ ] Backend logs show "Calculating confidence score"
- [ ] Badge appears in UI with color and percentage

---

## Nuclear Option: Hard-code for Testing

If absolutely nothing works, temporarily hard-code it:

**In `src/interfaces/rag_phi.py`**, change:
```python
if config.ENABLE_CONFIDENCE_SCORING:
```

To:
```python
if True:  # TEMP: Force enable
```

This will confirm if the issue is config loading or the feature itself.

---

## Expected Visual Result

Once working, you should see this in the UI:

```
┌────────────────────────────────────────────┐
│ What is the frequency response?            │ ← Your question
└────────────────────────────────────────────┘

The frequency response is 20Hz to 20kHz...    ← Answer

┌────────────────────────────────────────────┐
│ 🟢 Confidence: 87% │ HIGH                  │ ← This badge!
│ High confidence. Answer is based on...     │
└────────────────────────────────────────────┘

Sources (3 documents)
• Page 12 (specification)
...
```

The badge will be:
- **Green** for HIGH confidence (80-100%)
- **Orange** for MEDIUM confidence (60-80%)  
- **Red** for LOW confidence (0-60%)

---

## Get Help

If still not working after all steps:

1. Run diagnostic: `python scripts\test_enhancements.py`
2. Check `/api/test-confidence` endpoint
3. Share backend logs from startup
4. Share browser console output
5. Share API response from manual test

The issue is either:
- Config not loading (.env)
- System not restarted
- Cache serving old responses
- Feature calculation failing silently
