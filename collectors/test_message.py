
import asyncio
from datetime import timezone, datetime
from TikTokLive import TikTokLiveClient
from typing import Dict, Any

from TikTokLive.events import (
    ConnectEvent, 
    CommentEvent, 
    LikeEvent, 
    GiftEvent, 
    FollowEvent, 
    ShareEvent, 
    # ViewerCountUpdateEvent
)

name = ""
comment = ""
comment_count = 0
MAX_COMMENTS = 5
comments, usernames = [], []
stream_id = ""
host_id = ""
user_ids = []

ts_event_utc_mss = [] 
ts_events = []
comments_data = {
    "comments": [],
    "usernames": [],
    "ts_events": [],
    "ts_event_utc_mss": [],
}

# Create the client
client: TikTokLiveClient = TikTokLiveClient(unique_id="@bacgau1989")


# Listen to an event with a decorator!
@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"Connected to @{event.unique_id} (Room ID: {client.room_id}")
    global stream_id, host_id
    host_id = client.room_id
    stream_id = event.unique_id


# Or, add it manually via "client.add_listener()"
async def on_comment(event: CommentEvent) -> Dict[str, Any]:
    # print(f"{event.user.nickname} -> {event.comment}")
    global comment_count
    comment = event.comment
    if len(comment) > 10:
        comment_count += 1
        name = event.user.nickname
        user_ids.append(event.user.display_id)

        # Append the timestamp and user ID
        ts_event = datetime.now(timezone.utc).isoformat()
        ts_event_utc_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        ts_event_utc_mss.append(ts_event_utc_ms)
        ts_events.append(ts_event)

        print(f'TESTING {name} - {comment} - {comment_count} - {ts_event_utc_ms} - {ts_event}')
        print("=======================================")
        comments.append(comment)
        usernames.append(name)

    if comment_count >= MAX_COMMENTS - 1:
        await client.disconnect()
        await asyncio.sleep(2)

        # Get only data from the first comment to MAX_COMMENTS
        for i, key in enumerate(comments_data.keys()):
            print("Running here....")
            print(f"i is {i}, key is {key}")
            print(f"{comments[:MAX_COMMENTS]} - {usernames[:MAX_COMMENTS]} - {ts_events[:MAX_COMMENTS]} - {ts_event_utc_mss[:MAX_COMMENTS]}")
            if key == "comments":
                comments_data[key] = comments[:MAX_COMMENTS]
            elif key == "usernames":
                comments_data[key] = usernames[:MAX_COMMENTS]
            elif key == "ts_events":
                comments_data[key] = ts_events[:MAX_COMMENTS]
            elif key == "ts_event_utc_mss":
                comments_data[key] = ts_event_utc_mss[:MAX_COMMENTS]

        print(f"Stopped client after {MAX_COMMENTS} iterations")

        return comments_data
    


# async def on_gift(event: GiftEvent):
#     print(f"{event.user.uniqueId} sent a {event.gift.gift_id}!" )
#     for giftInfo in client.available_gifts:
#         if giftInfo["id"] == event.gift.gift_id:
#             print(f'Name: {giftInfo["name"]} - Image: {giftInfo["image"]["url_list"][0]} - Diamond: {giftInfo["diamond_count"]}')

# @client.on(LikeEvent)
# async def on_like(event: LikeEvent):
#     print(f"{event.user.unique_id} has liked the stream with the nickname {event.user.nickname}")


# @client.on(FollowEvent)
# async def on_follow(event: FollowEvent):
#     print(f"{event.user.unique_id} followed the streamer")

# @client.on(ShareEvent)
# async def on_share(event: ShareEvent):
#     print(f"{event.user.unique_id} shared the streamer!")


# @client.on("viewer_count_update")
# async def on_share(event: ViewerCountUpdateEvent):
#     print(f"Received a new viewer count: {event.viewerCount}")


client.add_listener(CommentEvent, on_comment)


async def main():
    await client.connect()

if __name__ == '__main__':
    # Run the client and block the main thread
    asyncio.run(main())

    print(f"Stream ID: {stream_id}")
    print(f"Host ID: {host_id}")
    # print(f"Comments: {comments}")
    # print(f"Usernames: {usernames}")
    print(f"AAll data after crawling from TikTok : \n {comments_data}")
