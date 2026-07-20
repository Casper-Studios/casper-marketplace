# PhantomBuster Setup

One-time setup to configure the LinkedIn Post Commenters phantom.

## Account & Pricing

Sign up at [phantombuster.com](https://www.phantombuster.com). Starter plan ($69/mo) is sufficient.
There's a 14-day free trial.

## Create the Phantom

1. Go to the [Phantom Store](https://phantombuster.com/phantoms)
2. Search for **"LinkedIn Post Commenters Export"** (also called "LinkedIn Post Commenter and Liker Scraper")
3. Click **"Use this Phantom"**

## Connect LinkedIn

The phantom needs your LinkedIn session cookie to browse LinkedIn on your behalf.

**Option A — Browser extension (recommended):**
1. Install the [PhantomBuster Chrome extension](https://chrome.google.com/webstore/detail/phantombuster/mdlnjfcpdiaclglfbdkbleiamdafilil)
2. Log into LinkedIn in Chrome
3. The extension auto-detects your `li_at` cookie

**Option B — Manual:**
1. Log into LinkedIn in Chrome
2. Open DevTools (F12) → Application → Cookies → `linkedin.com`
3. Find the `li_at` cookie and copy its value
4. Paste it into the PhantomBuster phantom's session cookie field

## Configure the Phantom

- Put any placeholder LinkedIn post URL (the script overrides this at runtime)
- Under "Engagers to extract", select **Commenters**
- Save the phantom

## Enable API Launch

**This is required** — without it the script gets a 412 error.

1. Open your phantom's settings
2. Go to the launch/schedule section
3. Enable **auto-launch** (either "Repeatedly" schedule or manual API launch)
4. Save

## Get Your Credentials

| Credential | Where |
|-----------|-------|
| **API Key** | [Settings → API](https://phantombuster.com/settings#api) |
| **Agent ID** | From the phantom URL: `phantombuster.com/phantoms/<AGENT_ID>/...` |

## Session Cookie Expiry

LinkedIn session cookies expire periodically (~30 days). If the scraper stops returning results,
refresh the cookie in PhantomBuster using the same process above.

## API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v2/agents/launch` | Launch the phantom with a post URL |
| `GET /api/v2/agents/fetch-output` | Poll for completion status |
| `GET /api/v2/agents/fetch` | Get S3 folder path for results |
| S3 download | Download the JSON result file |
