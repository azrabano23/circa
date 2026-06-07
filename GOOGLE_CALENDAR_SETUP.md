# Google Calendar Setup Fix

## ❌ The OAuth Error You're Seeing

**Error:** "mycal sent an invalid request"

**Why:** Your Google Cloud Console doesn't have the redirect URI registered.

---

## ✅ 3 Ways to Fix This

### Option 1: Use Calendar Feed (Easiest!)

**No OAuth needed!** Just subscribe to your Google Calendar:

1. **Get Calendar URL:**
   - Open Google Calendar in browser
   - Click Settings (gear icon)
   - Click "Settings" from menu
   - Select the calendar you want to sync
   - Scroll to "Integrate calendar"
   - Copy the "Secret address in iCal format"

2. **Add to Circa:**
   - Go to Settings → Integrations
   - Paste the calendar URL
   - Circa will fetch events automatically!

**Pros:** No OAuth setup needed, works immediately  
**Cons:** One-way sync (Google → Circa only)

---

### Option 2: Fix OAuth (Requires Google Cloud Console Access)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create one)
3. Go to **APIs & Services** → **Credentials**
4. Click on your OAuth 2.0 Client ID
5. Under **Authorized redirect URIs**, add:
   ```
   http://localhost:8000/api/v1/google/google/callback
   ```
6. Save changes
7. Wait 5 minutes for Google to propagate
8. Try connecting again in Circa!

**Pros:** Full bidirectional sync, can create events  
**Cons:** Requires Google Cloud Console setup

---

### Option 3: Manual Calendar Sync (Temporary Workaround)

For now, just manually add your important events in Circa:

1. Go to Calendar page in Circa
2. Click on date to add event
3. Or use AI Scheduler: "I have class Monday at 10 AM"

---

## 🎯 For Now: Use Option 1 (Calendar Feed)

This gives you automatic Google Calendar sync without OAuth hassle!

**Steps:**
1. Google Calendar → Settings → Your calendar
2. Scroll to "Integrate calendar"  
3. Copy "Secret address in iCal format"
4. In Circa → Settings → Paste URL
5. Done! Events sync automatically

---

## 💡 Better Alternative: Skip Google Calendar

Since you have OpenAI API working, use these instead:

### ✅ Canvas AI Import
- Copy/paste assignments from Canvas
- AI extracts everything
- **Working right now!**

### ✅ AI Natural Language Scheduler
- Type: "Class Monday 10 AM to 12 PM"
- Type: "Study session tomorrow 2 hours"
- AI adds to your calendar
- **Ready to use!**

### ✅ Manual Entry
- Add events in Calendar page
- Quick and works perfectly

---

**Recommendation:** Skip Google OAuth for now, use Canvas import and AI scheduler instead!

