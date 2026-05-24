//@version=6
strategy("NY ORB + EMA (Final with SL)", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

// ==============================
// ⚙️ USER INPUT
// ==============================
rrOption = input.string("1:1", title="Risk Reward", options=["1:1", "1:2"])
rr = rrOption == "1:1" ? 1.0 : 2.0

// ==============================
// 🕒 SESSION (AUTO DST)
// ==============================
sessionTime = "0930-1030"
timezone    = "America/New_York"

inSession = not na(time(timeframe.period, sessionTime, timezone))
sessionStart = inSession and not inSession[1]
sessionEnd   = not inSession and inSession[1]

// ==============================
// 📊 VARIABLES
// ==============================
var float sessionHigh = na
var float sessionLow  = na
var bool  tradeTaken  = false

// Reset daily
if sessionStart
    sessionHigh := high
    sessionLow  := low
    tradeTaken  := false

// Update range
if inSession
    sessionHigh := math.max(sessionHigh, high)
    sessionLow  := math.min(sessionLow, low)

// ==============================
// 📈 EMA
// ==============================
ema200 = ta.ema(close, 200)
plot(ema200, title="200 EMA", linewidth=2)

// ==============================
// 🚀 ENTRY CONDITIONS
// ==============================
afterSession = not inSession and not na(sessionHigh)

// STRICT BODY BREAKOUT
longBreak  = open > sessionHigh and close > sessionHigh
shortBreak = open < sessionLow  and close < sessionLow

longCondition  = afterSession and not tradeTaken and longBreak and close > ema200
shortCondition = afterSession and not tradeTaken and shortBreak and close < ema200

// Entries
if longCondition
    strategy.entry("BUY", strategy.long)
    tradeTaken := true

if shortCondition
    strategy.entry("SELL", strategy.short)
    tradeTaken := true

// ==============================
// 🎯 EXIT (SL = RANGE, TP = RR)
// ==============================
sessRange = sessionHigh - sessionLow

// LONG EXIT
if strategy.position_size > 0
    strategy.exit("Exit Buy", from_entry="BUY",
        stop = sessionLow,   // 🔴 YOUR RULE (SL = range low)
        limit = strategy.position_avg_price + (sessRange * rr))

// SHORT EXIT
if strategy.position_size < 0
    strategy.exit("Exit Sell", from_entry="SELL",
        stop = sessionHigh,  // 🔴 YOUR RULE (SL = range high)
        limit = strategy.position_avg_price - (sessRange * rr))

// ==============================
// 📦 BOX
// ==============================
var int startBar = na
var box sessionBox = na

if sessionStart
    startBar := bar_index

if sessionEnd
    sessionBox := box.new(
        left = startBar,
        right = bar_index,
        top = sessionHigh,
        bottom = sessionLow,
        border_color = color.yellow,
        border_width = 2,
        bgcolor = color.new(color.yellow, 85)
    )