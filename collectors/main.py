
from TikTokLive import TikTokLiveClient

from TikTokLive.events import (
    ConnectEvent, 
    CommentEvent, 
    LikeEvent, 
    GiftEvent, 
    FollowEvent, 
    ShareEvent, 
    ViewerCountUpdateEvent
)

# Create the client
client: TikTokLiveClient = TikTokLiveClient(unique_id="@kslow21")


# Listen to an event with a decorator!
@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"Connected to @{event.unique_id} (Room ID: {client.room_id}")


# Or, add it manually via "client.add_listener()"
async def on_comment(event: CommentEvent) -> None:
    print(f"{event.user.nickname} -> {event.comment}")

@client.on("gift")
async def on_gift(event: GiftEvent):
    print(f"{event.user.uniqueId} sent a {event.gift.gift_id}!" )
    for giftInfo in client.available_gifts:
        if giftInfo["id"] == event.gift.gift_id:
            print(f"Name: {giftInfo["name"]} - Image: {giftInfo["image"]["url_list"][0]} - Diamond: {giftInfo["diamond_count"]}")

@client.on("like")
async def on_like(event: LikeEvent):
    print(f"{event.user.uniqueId} has liked the stream {event.likeCount} times, there is now {event.totalLikeCount} total likes!")


@client.on("follow")
async def on_follow(event: FollowEvent):
    print(f"{event.user.uniqueId} followed the streamer")

@client.on("share")
async def on_share(event: ShareEvent):
    print(f"{event.user.uniqueId} shared the streamer!")


@client.on("viewer_count_update")
async def on_share(event: ViewerCountUpdateEvent):
    print(f"Received a new viewer count: {event.viewerCount}")


client.add_listener(CommentEvent, on_comment)

if __name__ == '__main__':
    # Run the client and block the main thread
    # await client.start() to run non-blocking
    client.run()
