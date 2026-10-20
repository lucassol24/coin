# Daily meme coin alert on Telegram

Every day this sends you up to 5 smaller, actively traded meme coins that are
up on the day. These are high risk. Most coins in this range lose value, and
some are rug pulls. The message links to CoinGecko and DexScreener and reminds
you to run rug checks.

## Setup (about 10 minutes, no cost)

### 1. Make a Telegram bot
1. In Telegram, open a chat with **@BotFather** and send `/newbot`.
2. Pick a name and a username ending in `bot`.
3. BotFather replies with a token. Keep it private. Anyone with it can post as your bot.

### 2. Get your chat id
1. Open your new bot in Telegram and press **Start**, then send it any message.
2. In a browser, open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   (replace `<YOUR_TOKEN>` with the token).
3. Find `"chat":{"id":123456789` in the result. That number is your chat id.

### 3. Put it on GitHub
1. Create a new **private** repository.
2. Upload `alert.py` and the `.github/workflows/daily.yml` file, keeping that folder path.
3. In the repo, go to **Settings > Secrets and variables > Actions > New repository secret** and add:
   - `TELEGRAM_BOT_TOKEN`: the token from step 1
   - `TELEGRAM_CHAT_ID`: the number from step 2

### 4. Test it
Go to the **Actions** tab, open **Daily meme coin alert**, and press **Run workflow**.
A message should arrive in Telegram within a minute. After that it runs daily at
14:00 UTC (9:00 AM Central until Nov 1, then 8:00 AM). Edit the `cron` line to change the time.

## Changing what it picks
The thresholds are at the top of `alert.py` (market cap range, minimum volume,
minimum turnover, maximum 24h gain, how many coins). Ranking is by turnover
(24h volume divided by market cap), among coins that are up on the day.

## Things to know
- It uses CoinGecko's free API without a key. If it ever returns an error for rate limits, the run just fails and tries again the next day.
- GitHub pauses scheduled runs on repos with no activity for 60 days. Press **Run workflow** once to restart it.
- Nothing here checks a coin's contract. CoinGecko data has no lock, holder or honeypot information, so you still have to check each coin yourself before buying.
- Not financial advice.

## Run it locally
`python3 alert.py --dry-run` prints the message without sending anything.
