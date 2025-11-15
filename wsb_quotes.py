"""
WSB Dark Humor Quotes and Sayings
For when your trades need some comedic relief
"""
import random

# Loading messages
LOADING_MESSAGES = [
    "Calculating your wife's boyfriend's gains...",
    "Consulting the magic 8-ball...",
    "Asking the Ouija board for financial advice...",
    "Checking Wendy's hiring status...",
    "Preparing your loss porn...",
    "Locating nearest dumpster behind Wendy's...",
    "Summoning the tendie gods...",
    "Analyzing crayon drawings...",
    "Converting hopium to copium...",
    "Calculating margin call probability...",
    "Checking if lambo or ramen tonight...",
    "Consulting r/wallstreetbets hivemind...",
]

# Buy signal messages
BUY_SIGNALS = {
    "strong_buy": [
        "🚀 YOLO TIME! This is more obvious than buying GME at $4!",
        "💎 DIAMOND HANDS ACTIVATED! Load up the truck!",
        "🦍 APE TOGETHER STRONG! This stock fucks!",
        "🌕 TO THE MOON! Your wife's boyfriend will be jealous!",
        "⚡ TENDIE ALERT! Better than FDs on a Friday!",
    ],
    "buy": [
        "✅ Looks promising, but DYOR (you won't tho)",
        "📊 Decent entry, not financial advice (wink wink)",
        "🎯 Could print, but I'm regarded so...",
        "💰 Solid play, unlike your last 10 trades",
        "🎲 Better odds than your 0DTE calls",
    ],
    "hold": [
        "🤔 Maybe wait? Or YOLO. I'm not your dad.",
        "⚠️ Ehh... flip a coin. 50/50 like all trades.",
        "📉 Not great, not terrible. Like your portfolio.",
        "🎰 Casino is that way ➡️",
        "😬 Your call, but Wendy's is hiring...",
    ],
    "sell": [
        "🔴 RUN! Faster than your dad went for cigarettes!",
        "💀 ABORT MISSION! Evacuate the Wendy's!",
        "🚨 This is more cursed than NFTs!",
        "❌ Hell nah! Even Cramer says avoid this one!",
        "⛔ Nope. Not even with your wife's boyfriend's money!",
    ]
}

# Sentiment messages
SENTIMENT_MESSAGES = {
    "bullish": [
        "Bulls are eating crayons tonight! 🖍️",
        "Apes are pounding their chests! 🦍",
        "This has more hopium than my last FD! 💊",
        "Everybody's girlfriend's boyfriend is buying!",
        "Even the bears are confused!",
    ],
    "bearish": [
        "Bears are feasting on ape tears 🐻",
        "More red than your portfolio YTD",
        "Copium levels: CRITICAL ⚠️",
        "Time to average down... again",
        "At least you have loss porn for karma",
    ],
    "neutral": [
        "Market is sideways like your life",
        "Even the bots are confused 🤖",
        "Theta gang eating good tonight",
        "Sounds like a cash gang moment",
        "Go outside, touch grass",
    ]
}

# Error messages
ERROR_MESSAGES = [
    "❌ Ticker not found. Did you make that up?",
    "🤡 Nice try. That's not a real ticker.",
    "💀 System error. Just like your last trade.",
    "⚠️ Something broke. Probably you.",
    "🚨 Error 404: Tendies not found",
    "😭 Failed harder than your calls last Friday",
]

# Dashboard taglines
DASHBOARD_TAGLINES = {
    "stocks": [
        "Where autism meets investing",
        "Diamond hands only beyond this point",
        "Your ticket to the moon... or Wendy's",
        "Technical analysis? Nah, we use crayons",
        "Positions or ban!",
    ],
    "options": [
        "Where money goes to die",
        "0DTE or nothing",
        "Maximum autism, maximum tendies",
        "The faster way to bankruptcy",
        "Your wife's boyfriend trades here",
    ],
    "crypto": [
        "Internet money go brrrrr",
        "69,420 is not a meme",
        "Have fun staying poor",
        "Decentralized degen gambling",
        "Not a cult (it's a cult)",
    ]
}

# Metric labels with humor
METRIC_LABELS = {
    "price": ["Current Copium Level", "What You're Bagholding At", "The Damage"],
    "change": ["Pain Level", "Gain/Loss Porn", "Today's Character Building"],
    "volume": ["How Many Regards Trading", "Ape Activity Level", "Market FOMO Index"],
    "market_cap": ["Size of the Casino", "Total Gamble Value", "How Big Can We Pump This"],
    "pe_ratio": ["Overvalued By", "Boomer Metric", "Traditional Cope Ratio"],
    "target": ["Hopium Price Target", "Where Lambo Lives", "Theoretical Moon Landing"],
    "stop_loss": ["Panic Sell Here", "Weak Hands Exit", "Paper Hands Portal"],
}

# Technical analysis commentary
TECHNICAL_COMMENTS = {
    "rsi_oversold": [
        "RSI lower than your self-esteem!",
        "This thing is more oversold than my dignity",
        "Buy signal stronger than grandpa's aftershave",
    ],
    "rsi_overbought": [
        "Overbought like it's Black Friday at GameStop",
        "Time to take profits (you won't tho)",
        "Higher than Snoop Dogg on 4/20",
    ],
    "macd_bullish": [
        "MACD crossed over like my eyes after margin call",
        "Bullish af, even smooth brains can see it",
        "Lines go up = money go up (trust me bro)",
    ],
    "macd_bearish": [
        "MACD going down faster than your account",
        "Bearish cross detected. Press F to pay respects.",
        "Lines going down, just like my hope",
    ],
    "support": [
        "Support level: Last stand before bankruptcy",
        "This is where dreams go to bounce",
        "Support here thicc like my skull",
    ],
    "resistance": [
        "Resistance stronger than my will to hold",
        "This ceiling harder to break than my bad habits",
        "Resistance level: Where gains go to die",
    ]
}

# Options specific
OPTIONS_COMMENTS = {
    "high_iv": [
        "IV so high, even Snoop is impressed",
        "Premium thicc, theta gang salivating",
        "IV crush incoming faster than your dad",
    ],
    "low_iv": [
        "IV lower than my expectations",
        "Cheaper than Costco hotdogs",
        "IV so low, boomers might buy it",
    ],
    "unusual_volume": [
        "Someone knows something... or YOLO'd their rent",
        "Volume spike! Insider or idiot? Yes.",
        "Unusual activity detected. Nancy Pelosi entered the chat.",
    ],
}

# Crypto specific
CRYPTO_COMMENTS = {
    "bullish": [
        "Number go up technology in action",
        "This is good for Bitcoin (everything is)",
        "WAGMI (We All Gonna Make It)... probably not",
    ],
    "bearish": [
        "Have fun staying poor",
        "Zoom out bro (no seriously, zoom way out)",
        "Buy the dip (the 47th dip this week)",
    ],
    "hodl": [
        "HODL! Can't lose if you don't sell (taps head)",
        "Diamond hands since $69k",
        "Not selling until $420k minimum",
    ]
}

def get_random_message(category, subcategory=None):
    """Get a random WSB message"""
    if subcategory:
        if category in globals() and subcategory in globals()[category]:
            messages = globals()[category][subcategory]
            return random.choice(messages)
    elif category in globals():
        messages = globals()[category]
        if isinstance(messages, dict):
            all_msgs = []
            for msgs in messages.values():
                all_msgs.extend(msgs)
            return random.choice(all_msgs)
        else:
            return random.choice(messages)
    return "🚀 TO THE MOON!"

def get_confidence_message(score):
    """Get message based on confidence score"""
    if score >= 80:
        return random.choice(BUY_SIGNALS["strong_buy"])
    elif score >= 60:
        return random.choice(BUY_SIGNALS["buy"])
    elif score >= 40:
        return random.choice(BUY_SIGNALS["hold"])
    else:
        return random.choice(BUY_SIGNALS["sell"])

def get_loading_message():
    """Get random loading message"""
    return random.choice(LOADING_MESSAGES)

def get_dashboard_tagline(dashboard_type):
    """Get tagline for dashboard"""
    if dashboard_type in DASHBOARD_TAGLINES:
        return random.choice(DASHBOARD_TAGLINES[dashboard_type])
    return "YOLO or go home"

def get_metric_label(metric_type):
    """Get funny label for metric"""
    if metric_type in METRIC_LABELS:
        return random.choice(METRIC_LABELS[metric_type])
    return metric_type.title()

def get_error_message():
    """Get random error message"""
    return random.choice(ERROR_MESSAGES)

def get_sentiment_comment(sentiment_type):
    """Get sentiment commentary"""
    if sentiment_type in SENTIMENT_MESSAGES:
        return random.choice(SENTIMENT_MESSAGES[sentiment_type])
    return "Market be crazy 🤪"

def get_technical_comment(indicator_type):
    """Get technical indicator comment"""
    if indicator_type in TECHNICAL_COMMENTS:
        return random.choice(TECHNICAL_COMMENTS[indicator_type])
    return "Lines on chart go brrr"

def get_options_comment(comment_type):
    """Get options specific comment"""
    if comment_type in OPTIONS_COMMENTS:
        return random.choice(OPTIONS_COMMENTS[comment_type])
    return "May the Greeks be with you"

def get_crypto_comment(comment_type):
    """Get crypto specific comment"""
    if comment_type in CRYPTO_COMMENTS:
        return random.choice(CRYPTO_COMMENTS[comment_type])
    return "GM (Good Morning) ☀️"
