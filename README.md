# Metallum Informant Telegram
This is the Telegram version of the Metallum Informant bot.

A bot that queries the [Encyclopaedia Metallum](www.metal-archives.com)[^1] for metal bands and shows the results to the user.

Also available for Discord: https://github.com/Pedro-HMV/metallum-discord-bot.

## Third-party packages
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot), a Python API wrapper for Telegram.

- [python-metallum](https://github.com/Pedro-HMV/python-metallum), a Python API for the Encyclopaedia Metallum.
  - I use my own fork for this, since the original hasn't been maintained in a while and had a broken import[^2].

## Python
Python 3.8 is recommended for guaranteed compatibility.

You also need to create a file named `.env` and store your bot's secret token in a variable there like so: `BOT_TOKEN="AIpodj83u1hsdahfoUHA:dashuioda.das1123.d281ue"`.  
   - Replace the string inside quotes with you bot's token.

## Usage
1. Find the bot in Telegram by its username @MetalumBot (Metallum was taken) or via [this link](https://t.me/metalumbot).
2. The commands are as follow:
```
/start -> basic info and instructions

/band <band name> -> a strict search (exact match) e.g. /band iron maiden

/bands <search words> -> advanced search (lots of options, check the help for this command) e.g. /bands *iron* maiden || black* -sabbath

/help band -> more info on the /band command

/help bands -> more info on the /bands command

/stop -> stop an ongoing search (in case there's too many results and you don't wanna get them anymore)
```
  - Please use `/help band` and `/help bands` to see the [detailed explanations](#help-screenshots).
### Basic examples:
#### command
`/band black sabbath`
#### result
```
Black Sabbath

GENRES: Heavy/Doom Metal

LOCATION: Birmingham, West Midlands, England, United Kingdom

FORMED IN: 1969

STATUS: Split-up

THEMES: Doom, Drugs, Life, Death, Religion

ALBUMS: 
(1970) Black Sabbath
(1970) Paranoid
(1971) Master of Reality
(1972) Black Sabbath Vol. 4
(1973) Sabbath Bloody Sabbath
(1975) Sabotage
(1976) Technical Ecstasy
(1978) Never Say Die!
(1980) Heaven and Hell
(1981) Mob Rules
(1983) Born Again
(1986) Seventh Star
(1987) The Eternal Idol
(1989) Headless Cross
(1990) Tyr
(1992) Dehumanizer
(1994) Cross Purposes
(1995) Forbidden
(2013) 13

PAGE: https://metal-archives.com/bands/_/99

1/1
```

#### command
`/bands black sabbath`
#### result
```
Black Sabbath

GENRES: Heavy/Doom Metal

LOCATION: Birmingham, West Midlands, England, United Kingdom

FORMED IN: 1969

STATUS: Split-up

THEMES: Doom, Drugs, Life, Death, Religion

ALBUMS: 
(1970) Black Sabbath
(1970) Paranoid
(1971) Master of Reality
(1972) Black Sabbath Vol. 4
(1973) Sabbath Bloody Sabbath
(1975) Sabotage
(1976) Technical Ecstasy
(1978) Never Say Die!
(1980) Heaven and Hell
(1981) Mob Rules
(1983) Born Again
(1986) Seventh Star
(1987) The Eternal Idol
(1989) Headless Cross
(1990) Tyr
(1992) Dehumanizer
(1994) Cross Purposes
(1995) Forbidden
(2013) 13

PAGE: https://metal-archives.com/bands/_/99

1/2

******************************

Sabbath Black Heretic

GENRES: Symphonic Gothic/Power Metal

LOCATION: Tokyo, Japan

FORMED IN: 2013

STATUS: Changed name

THEMES: N/A

ALBUMS: 
This band has no full-length albums. Check their page below for other releases.

PAGE: https://metal-archives.com/bands/_/3540442557

2/2
```

## /help screenshots
#### /help band
![image](https://user-images.githubusercontent.com/85079897/161806736-b5808363-2026-4699-9d39-bb60a45e395b.png)
#### /help bands
![image](https://user-images.githubusercontent.com/85079897/161806923-aaa8ca11-9dbb-4852-8f20-a6a161fb70b1.png)


[^1]: A website with a huge database of metal bands.
  https://metal-archives.com.
[^2]: The original python-metallum package can be found [here](https://github.com/lcharlick/python-metallum).  
  The problem is that it hasn't received updates in over a year and has a broken import which raises an error and prevents the whole package from working.  
  So to avoid having to manually fix he issue on every new installation, and especially when deploying, I decided to fork it and use my own fixed version.
