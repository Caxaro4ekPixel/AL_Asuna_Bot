from asuna_bot.db.odm.release import Release
from datetime import datetime


class TimerTest:
    @staticmethod
    async def test_timer():
        all_ongoings = await Release.get_all_ongoings()
        for release in all_ongoings:
            last_ep = release.episodes[list(release.episodes)[-1]]
            time_delta = datetime.now() - last_ep.date
            if (time_delta.total_seconds() / 3600) % 6 == 0:
                print(f"Last episode: {last_ep.title}")
