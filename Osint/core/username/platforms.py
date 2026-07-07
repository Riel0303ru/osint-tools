# core/username/platforms.py
"""
Daftar platform OSINT untuk pengecekan username.
Setiap entri dapat memiliki field opsional:
- content_required : string yang harus muncul di halaman (format dengan username)
- content_forbidden: string yang TIDAK BOLEH muncul (misal "Page not found")
Gunakan { } sebagai placeholder untuk username.
"""

PLATFORMS = [
    # =========================================================
    # SOCIAL MEDIA & MESSAGING (prioritas tinggi – divalidasi)
    # =========================================================
    {
        "name": "Instagram",
        "url": "https://www.instagram.com/{}",
        "method": "GET",
        "status_codes": [200],
        "content_required": '"username":"{}"',
        "content_forbidden": "Sorry, this page isn't available",
    },
    {
        "name": "TikTok",
        "url": "https://www.tiktok.com/@{}",
        "method": "GET",
        "status_codes": [200],
        "content_required": '"nickname":"{}"',
        "content_forbidden": "Couldn't find this account",
    },
    {
        "name": "X (Twitter)",
        "url": "https://x.com/{}",
        "method": "GET",
        "status_codes": [200],
        "content_required": 'screen_name":"{}"',
        "content_forbidden": "This account doesn’t exist",
    },
    {
        "name": "Facebook",
        "url": "https://www.facebook.com/{}",
        "method": "GET",
        "status_codes": [200],
        "content_required": '{"name":"{}"',
        "content_forbidden": "This page isn't available",
    },
    {
        "name": "LinkedIn",
        "url": "https://www.linkedin.com/in/{}",
        "method": "GET",
        "status_codes": [200],
        "content_required": "{} | LinkedIn",
        "content_forbidden": "Page not found",
    },
    {
        "name": "Reddit",
        "url": "https://www.reddit.com/user/{}",
        "method": "GET",
        "status_codes": [200],
        "content_required": "u/{}",
        "content_forbidden": "Sorry, nobody on Reddit goes by that name",
    },
    {
        "name": "Pinterest",
        "url": "https://www.pinterest.com/{}/",
        "method": "GET",
        "status_codes": [200],
        "content_required": '"username":"{}"',
        "content_forbidden": "Page not found",
    },
    {
        "name": "Tumblr",
        "url": "https://{}.tumblr.com",
        "method": "GET",
        "status_codes": [200],
        "content_required": '<meta name="author" content="{}"',
        "content_forbidden": "Not found",
    },
    # Sisanya tanpa validasi konten (tetap aman dengan status code)
    {"name": "Telegram", "url": "https://t.me/{}", "method": "GET", "status_codes": [200]},
    {"name": "Discord", "url": "https://discord.com/api/v9/users/{}", "method": "GET", "status_codes": [200]},
    {"name": "Snapchat", "url": "https://www.snapchat.com/add/{}", "method": "GET", "status_codes": [200]},
    {"name": "VK", "url": "https://vk.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Mastodon", "url": "https://mastodon.social/@{}", "method": "GET", "status_codes": [200]},
    {"name": "Minds", "url": "https://www.minds.com/{}/", "method": "GET", "status_codes": [200]},
    {"name": "Gab", "url": "https://gab.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Gettr", "url": "https://gettr.com/user/{}", "method": "GET", "status_codes": [200]},
    {"name": "Vero", "url": "https://vero.co/{}", "method": "GET", "status_codes": [200]},
    {"name": "Kik", "url": "https://kik.me/{}", "method": "GET", "status_codes": [200]},

    # =========================================================
    # DEVELOPERS & TECH (GitHub, GitLab, StackExchange, dll.)
    # =========================================================
    {
        "name": "GitHub",
        "url": "https://github.com/{}",
        "method": "GET",
        "status_codes": [200],
        "content_required": "{} · GitHub",
        "content_forbidden": "Page not found",
    },
    {
        "name": "GitLab",
        "url": "https://gitlab.com/{}",
        "method": "GET",
        "status_codes": [200],
        "content_required": '<meta property="og:title" content="{}',
        "content_forbidden": "Sign in",
    },
    # Untuk lainnya, biarkan default
    {"name": "Bitbucket", "url": "https://bitbucket.org/{}/", "method": "GET", "status_codes": [200]},
    {"name": "Gitea", "url": "https://gitea.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Codeberg", "url": "https://codeberg.org/{}", "method": "GET", "status_codes": [200]},
    {"name": "SourceForge", "url": "https://sourceforge.net/u/{}/profile", "method": "GET", "status_codes": [200]},
    {"name": "Kaggle", "url": "https://www.kaggle.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Codecademy", "url": "https://www.codecademy.com/profiles/{}", "method": "GET", "status_codes": [200]},
    {"name": "HackerRank", "url": "https://www.hackerrank.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "HackerEarth", "url": "https://www.hackerearth.com/@{}", "method": "GET", "status_codes": [200]},
    {"name": "LeetCode", "url": "https://leetcode.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Codewars", "url": "https://www.codewars.com/users/{}", "method": "GET", "status_codes": [200]},
    {"name": "Replit", "url": "https://replit.com/@{}", "method": "GET", "status_codes": [200]},
    {"name": "CodePen", "url": "https://codepen.io/{}", "method": "GET", "status_codes": [200]},
    {"name": "JSFiddle", "url": "https://jsfiddle.net/user/{}", "method": "GET", "status_codes": [200]},
    {"name": "CRAN", "url": "https://cran.r-project.org/package={}", "method": "GET", "status_codes": [200]},
    {"name": "npm", "url": "https://www.npmjs.com/~{}", "method": "GET", "status_codes": [200]},
    {"name": "PyPI", "url": "https://pypi.org/user/{}", "method": "GET", "status_codes": [200]},
    {"name": "Docker Hub", "url": "https://hub.docker.com/u/{}", "method": "GET", "status_codes": [200]},
    {"name": "Postman", "url": "https://www.postman.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Dev.to", "url": "https://dev.to/{}", "method": "GET", "status_codes": [200]},
    {"name": "Hashnode", "url": "https://hashnode.com/@{}", "method": "GET", "status_codes": [200]},
    {"name": "Zenn", "url": "https://zenn.dev/{}", "method": "GET", "status_codes": [200]},
    {"name": "FreeCodeCamp", "url": "https://www.freecodecamp.org/{}", "method": "GET", "status_codes": [200]},
    {"name": "Apple Developer", "url": "https://developer.apple.com/forums/profile/{}", "method": "GET", "status_codes": [200]},

    # =========================================================
    # CYBER SECURITY & BUG BOUNTY
    # =========================================================
    {"name": "TryHackMe", "url": "https://tryhackme.com/p/{}", "method": "GET", "status_codes": [200]},
    {"name": "HackerOne", "url": "https://hackerone.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Bugcrowd", "url": "https://bugcrowd.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Bountysource", "url": "https://www.bountysource.com/users/{}", "method": "GET", "status_codes": [200]},

    # =========================================================
    # VIDEO, STREAMING & AUDIO
    # =========================================================
    {
        "name": "YouTube",
        "url": "https://www.youtube.com/@{}",
        "method": "GET",
        "status_codes": [200],
        "content_required": '"name":"{}"',
        "content_forbidden": "This channel does not exist",
    },
    {"name": "Twitch", "url": "https://www.twitch.tv/{}", "method": "GET", "status_codes": [200]},
    {"name": "Kick", "url": "https://kick.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Vimeo", "url": "https://vimeo.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Dailymotion", "url": "https://www.dailymotion.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Spotify", "url": "https://open.spotify.com/user/{}", "method": "GET", "status_codes": [200]},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Mixcloud", "url": "https://www.mixcloud.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Bandcamp", "url": "https://{}.bandcamp.com", "method": "GET", "status_codes": [200]},
    {"name": "ReverbNation", "url": "https://www.reverbnation.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Last.fm", "url": "https://www.last.fm/user/{}", "method": "GET", "status_codes": [200]},
    {"name": "Discogs", "url": "https://www.discogs.com/user/{}", "method": "GET", "status_codes": [200]},
    {"name": "Periscope", "url": "https://www.periscope.tv/{}", "method": "GET", "status_codes": [200]},
    {"name": "BitChute", "url": "https://www.bitchute.com/channel/{}/", "method": "GET", "status_codes": [200]},
    {"name": "Odysee", "url": "https://odysee.com/@{}", "method": "GET", "status_codes": [200]},
    {"name": "Rumble", "url": "https://rumble.com/user/{}", "method": "GET", "status_codes": [200]},
    {"name": "Mixer", "url": "https://mixer.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Smule", "url": "https://www.smule.com/{}", "method": "GET", "status_codes": [200]},

    # =========================================================
    # GAMING
    # =========================================================
    {"name": "Steam", "url": "https://steamcommunity.com/id/{}", "method": "GET", "status_codes": [200]},
    {"name": "Roblox", "url": "https://www.roblox.com/user.aspx?username={}", "method": "GET", "status_codes": [200]},
    {"name": "Xbox Gamertag", "url": "https://xboxgamertag.com/search/{}", "method": "GET", "status_codes": [200]},
    {"name": "Speedrun", "url": "https://www.speedrun.com/user/{}", "method": "GET", "status_codes": [200]},
    {"name": "Osu!", "url": "https://osu.ppy.sh/users/{}", "method": "GET", "status_codes": [200]},
    {"name": "Chess.com", "url": "https://www.chess.com/member/{}", "method": "GET", "status_codes": [200]},
    {"name": "Lichess", "url": "https://lichess.org/@/{}", "method": "GET", "status_codes": [200]},

    # =========================================================
    # DESIGN, ART & PHOTOGRAPHY
    # =========================================================
    {"name": "Dribbble", "url": "https://dribbble.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Behance", "url": "https://www.behance.net/{}", "method": "GET", "status_codes": [200]},
    {"name": "DeviantArt", "url": "https://www.deviantart.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "ArtStation", "url": "https://www.artstation.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Flickr", "url": "https://www.flickr.com/people/{}", "method": "GET", "status_codes": [200]},
    {"name": "500px", "url": "https://500px.com/p/{}", "method": "GET", "status_codes": [200]},
    {"name": "VSCO", "url": "https://vsco.co/{}", "method": "GET", "status_codes": [200]},
    {"name": "Pixabay", "url": "https://pixabay.com/users/{}", "method": "GET", "status_codes": [200]},
    {"name": "Unsplash", "url": "https://unsplash.com/@{}", "method": "GET", "status_codes": [200]},
    {"name": "Pexels", "url": "https://www.pexels.com/@{}", "method": "GET", "status_codes": [200]},
    {"name": "Canva", "url": "https://www.canva.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Coroflot", "url": "https://www.coroflot.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Figma", "url": "https://www.figma.com/@{}", "method": "GET", "status_codes": [200]},
    {"name": "Imgur", "url": "https://imgur.com/user/{}", "method": "GET", "status_codes": [200]},
    {"name": "Imgflip", "url": "https://imgflip.com/user/{}", "method": "GET", "status_codes": [200]},

    # =========================================================
    # BLOGGING, WRITING & READING
    # =========================================================
    {
        "name": "Medium",
        "url": "https://medium.com/@{}",
        "method": "GET",
        "status_codes": [200],
        "content_required": 'property="og:title" content="{}',
        "content_forbidden": "User not found",
    },
    {"name": "Substack", "url": "https://{}.substack.com", "method": "GET", "status_codes": [200]},
    {"name": "WordPress", "url": "https://{}.wordpress.com", "method": "GET", "status_codes": [200]},
    {"name": "Blogger", "url": "https://{}.blogspot.com", "method": "GET", "status_codes": [200]},
    {"name": "LiveJournal", "url": "https://{}.livejournal.com", "method": "GET", "status_codes": [200]},
    {"name": "Wattpad", "url": "https://www.wattpad.com/user/{}", "method": "GET", "status_codes": [200]},
    {"name": "Quora", "url": "https://www.quora.com/profile/{}", "method": "GET", "status_codes": [200]},
    {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/User:{}", "method": "GET", "status_codes": [200]},
    {"name": "SlideShare", "url": "https://www.slideshare.net/{}", "method": "GET", "status_codes": [200]},
    {"name": "Academia.edu", "url": "https://independent.academia.edu/{}", "method": "GET", "status_codes": [200]},
    {"name": "Issuu", "url": "https://issuu.com/{}", "method": "GET", "status_codes": [200]},

    # =========================================================
    # MOVIES, ANIME & ENTERTAINMENT
    # =========================================================
    {"name": "MyAnimeList", "url": "https://myanimelist.net/profile/{}", "method": "GET", "status_codes": [200]},
    {"name": "Anilist", "url": "https://anilist.co/user/{}/", "method": "GET", "status_codes": [200]},
    {"name": "Letterboxd", "url": "https://letterboxd.com/{}/", "method": "GET", "status_codes": [200]},
    {"name": "Trakt", "url": "https://trakt.tv/users/{}", "method": "GET", "status_codes": [200]},
    {"name": "RateYourMusic", "url": "https://rateyourmusic.com/~{}", "method": "GET", "status_codes": [200]},
    {"name": "Fandom", "url": "https://www.fandom.com/u/{}", "method": "GET", "status_codes": [200]},

    # =========================================================
    # FUNDING, COMMERCE & FREELANCE
    # =========================================================
    {"name": "Patreon", "url": "https://www.patreon.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Ko-fi", "url": "https://ko-fi.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "BuyMeACoffee", "url": "https://www.buymeacoffee.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Gumroad", "url": "https://gumroad.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Fiverr", "url": "https://www.fiverr.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Upwork", "url": "https://www.upwork.com/freelancers/~{}", "method": "GET", "status_codes": [200]},
    {"name": "Etsy", "url": "https://www.etsy.com/people/{}", "method": "GET", "status_codes": [200]},
    {"name": "eBay", "url": "https://www.ebay.com/usr/{}", "method": "GET", "status_codes": [200]},
    {"name": "Depop", "url": "https://www.depop.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Vinted", "url": "https://www.vinted.com/member/{}", "method": "GET", "status_codes": [200]},
    {"name": "CreativeMarket", "url": "https://creativemarket.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Zazzle", "url": "https://www.zazzle.com/mbr/{}", "method": "GET", "status_codes": [200]},
    {"name": "Society6", "url": "https://society6.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Redbubble", "url": "https://www.redbubble.com/people/{}", "method": "GET", "status_codes": [200]},
    {"name": "Venmo", "url": "https://account.venmo.com/u/{}", "method": "GET", "status_codes": [200]},
    {"name": "OpenSea", "url": "https://opensea.io/{}", "method": "GET", "status_codes": [200]},

    # =========================================================
    # PROFILE AGGREGATORS & LINKS
    # =========================================================
    {"name": "Linktree", "url": "https://linktr.ee/{}", "method": "GET", "status_codes": [200]},
    {"name": "About.me", "url": "https://about.me/{}", "method": "GET", "status_codes": [200]},
    {"name": "Carrd", "url": "https://{}.carrd.co/", "method": "GET", "status_codes": [200]},
    {"name": "Polywork", "url": "https://www.polywork.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Pronouns.page", "url": "https://en.pronouns.page/@{}", "method": "GET", "status_codes": [200]},

    # =========================================================
    # OTHERS (COMMUNITY, TRAVEL, 3D, ETC.)
    # =========================================================
    {"name": "Keybase", "url": "https://keybase.io/{}", "method": "GET", "status_codes": [200]},
    {"name": "AskFM", "url": "https://ask.fm/{}", "method": "GET", "status_codes": [200]},
    {"name": "Peing", "url": "https://peing.net/en/{}", "method": "GET", "status_codes": [200]},
    {"name": "ProductHunt", "url": "https://www.producthunt.com/@{}", "method": "GET", "status_codes": [200]},
    {"name": "AngelList", "url": "https://angel.co/u/{}", "method": "GET", "status_codes": [200]},
    {"name": "Foursquare", "url": "https://foursquare.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Houzz", "url": "https://houzz.com/user/{}", "method": "GET", "status_codes": [200]},
    {"name": "We Heart It", "url": "https://weheartit.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Badoo", "url": "https://badoo.com/en/{}", "method": "GET", "status_codes": [200]},
    {"name": "Myspace", "url": "https://myspace.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Vine", "url": "https://vine.co/{}", "method": "GET", "status_codes": [200]},
    {"name": "Pastebin", "url": "https://pastebin.com/u/{}", "method": "GET", "status_codes": [200]},
    {"name": "Trello", "url": "https://trello.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Notion", "url": "https://{}.notion.site", "method": "GET", "status_codes": [200]},
    {"name": "Gravatar", "url": "https://en.gravatar.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "TripAdvisor", "url": "https://www.tripadvisor.com/Profile/{}", "method": "GET", "status_codes": [200]},
    {"name": "CouchSurfing", "url": "https://www.couchsurfing.com/people/{}", "method": "GET", "status_codes": [200]},
    {"name": "AllTrails", "url": "https://www.alltrails.com/members/{}", "method": "GET", "status_codes": [200]},
    {"name": "Thingiverse", "url": "https://www.thingiverse.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Cults3D", "url": "https://cults3d.com/en/users/{}", "method": "GET", "status_codes": [200]},
    {"name": "Instructables", "url": "https://www.instructables.com/member/{}/", "method": "GET", "status_codes": [200]},
    {"name": "Hackaday", "url": "https://hackaday.io/{}", "method": "GET", "status_codes": [200]},
    {"name": "TradingView", "url": "https://www.tradingview.com/u/{}/", "method": "GET", "status_codes": [200]},
    {"name": "Quizlet", "url": "https://quizlet.com/{}", "method": "GET", "status_codes": [200]},
    {"name": "Scratch", "url": "https://scratch.mit.edu/users/{}/", "method": "GET", "status_codes": [200]},
]