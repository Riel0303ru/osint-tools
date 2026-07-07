from __future__ import annotations

from typing import Dict, List, Optional

from core.base.base_scanner import BaseScanner


class UsernameScanner(BaseScanner):


    def __init__(
        self,
        base_dir: str = "Osint"
    ):

        super().__init__(
            base_dir=base_dir
        )
        
        self.platforms = {


            "GitHub": {
                "url": "https://github.com/{}",
                "category": "development",
                "method": "HEAD",
            },

            "GitLab": {
                "url": "https://gitlab.com/{}",
                "category": "development",
                "method": "HEAD",
            },

            "Bitbucket": {
                "url": "https://bitbucket.org/{}",
                "category": "development",
                "method": "HEAD",
            },

            "Kaggle": {
                "url": "https://www.kaggle.com/{}",
                "category": "development",
                "method": "GET",
            },

            "LeetCode": {
                "url": "https://leetcode.com/{}",
                "category": "development",
                "method": "GET",
            },

            "HackerRank": {
                "url": "https://www.hackerrank.com/{}",
                "category": "development",
                "method": "GET",
            },

            "CodePen": {
                "url": "https://codepen.io/{}",
                "category": "development",
                "method": "HEAD",
            },

            "Replit": {
                "url": "https://replit.com/@{}",
                "category": "development",
                "method": "GET",
            },

            "DockerHub": {
                "url": "https://hub.docker.com/u/{}",
                "category": "development",
                "method": "GET",
            },

            "Instagram": {
                "url": "https://www.instagram.com/{}/",
                "category": "social",
                "method": "GET",
            },

            "Threads": {
                "url": "https://www.threads.net/@{}",
                "category": "social",
                "method": "GET",
            },

            "TikTok": {
                "url": "https://www.tiktok.com/@{}",
                "category": "social",
                "method": "GET",
            },

            "Reddit": {
                "url": "https://www.reddit.com/user/{}",
                "category": "social",
                "method": "HEAD",
            },

            "Pinterest": {
                "url": "https://www.pinterest.com/{}/",
                "category": "social",
                "method": "HEAD",
            },

            "Tumblr": {
                "url": "https://{}.tumblr.com",
                "category": "social",
                "method": "GET",
            },

            "VSCO": {
                "url": "https://vsco.co/{}/gallery",
                "category": "social",
                "method": "GET",
            },

            "Flickr": {
                "url": "https://www.flickr.com/people/{}",
                "category": "social",
                "method": "HEAD",
            },

            "Facebook": {
                "url": "https://www.facebook.com/{}",
                "category": "social",
                "method": "GET",
            },

            "X": {
                "url": "https://x.com/{}",
                "category": "social",
                "method": "GET",
            },

            "LinkedIn": {
                "url": "https://www.linkedin.com/in/{}",
                "category": "professional",
                "method": "GET",
            },

            "Telegram": {
                "url": "https://t.me/{}",
                "category": "communication",
                "method": "HEAD",
            },

            "Discord": {
                "url": "https://discord.com/users/{}",
                "category": "communication",
                "method": "GET",
            },

            "Steam": {
                "url": "https://steamcommunity.com/id/{}",
                "category": "gaming",
                "method": "HEAD",
            },

            "Roblox": {
                "url": "https://www.roblox.com/user.aspx?username={}",
                "category": "gaming",
                "method": "GET",
            },

            "Chess.com": {
                "url": "https://www.chess.com/member/{}",
                "category": "gaming",
                "method": "HEAD",
            },

            "Twitch": {
                "url": "https://www.twitch.tv/{}",
                "category": "gaming",
                "method": "HEAD",
            },

            "Spotify": {
                "url": "https://open.spotify.com/user/{}",
                "category": "music",
                "method": "GET",
            },

            "SoundCloud": {
                "url": "https://soundcloud.com/{}",
                "category": "music",
                "method": "HEAD",
            },

            "Bandcamp": {
                "url": "https://{}.bandcamp.com",
                "category": "music",
                "method": "GET",
            },

            "LastFM": {
                "url": "https://www.last.fm/user/{}",
                "category": "music",
                "method": "HEAD",
            },

            "Medium": {
                "url": "https://medium.com/@{}",
                "category": "content",
                "method": "HEAD",
            },

            "YouTube": {
                "url": "https://www.youtube.com/@{}",
                "category": "content",
                "method": "GET",
            },

            "Patreon": {
                "url": "https://www.patreon.com/{}",
                "category": "content",
                "method": "GET",
            },

            "DeviantArt": {
                "url": "https://www.deviantart.com/{}",
                "category": "content",
                "method": "HEAD",
            },

            "Fiverr": {
                "url": "https://www.fiverr.com/{}",
                "category": "freelance",
                "method": "GET",
            },

            "Behance": {
                "url": "https://www.behance.net/{}",
                "category": "freelance",
                "method": "HEAD",
            },

            "Dribbble": {
                "url": "https://dribbble.com/{}",
                "category": "freelance",
                "method": "HEAD",
            },

            "Pastebin": {
                "url": "https://pastebin.com/u/{}",
                "category": "misc",
                "method": "GET",
            },

            "Linktree": {
                "url": "https://linktr.ee/{}",
                "category": "misc",
                "method": "GET",
            },

            "AboutMe": {
                "url": "https://about.me/{}",
                "category": "misc",
                "method": "GET",
            },

            "Gravatar": {
                "url": "https://gravatar.com/{}",
                "category": "misc",
                "method": "HEAD",
            },
        }

    def get_available_platforms(
        self
    ) -> List[str]:
        """
        Get all platform names.
        """

        return list(
            self.platforms.keys()
        )

    def get_platform_data(
        self,
        platform_name: str
    ) -> Optional[Dict]:
        """
        Get platform metadata.
        """

        return self.platforms.get(
            platform_name
        )

    def build_profile_url(
        self,
        platform_name: str,
        username: str
    ) -> str:
        """
        Build profile URL.
        """

        platform_data = (
            self.get_platform_data(
                platform_name
            )
        )

        if not platform_data:

            raise ValueError(
                (
                    f"Platform "
                    f"'{platform_name}' "
                    f"not found."
                )
            )

        return platform_data[
            "url"
        ].format(username)

    def create_result(
        self,
        module_name: str,
        target: str,
        status: str,
        url: Optional[str] = None,
        details: Optional[Dict] = None,
    ) -> Dict:
        """
        Standardized result structure.
        """

        return {
            "module": module_name,
            "target": target,
            "status": status,
            "url": url,
            "details": details or {},
        }