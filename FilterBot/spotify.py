import requests
import os
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pyrogram import Client, filters
from pyrogram.types import Message

# Initialize Spotify API credentials
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.environ.get("SPOTIPY_CLIENT_ID"), client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET")))

# enable logging
logging.basicConfig(level=logging.DEBUG)


# initialize the Spotify API client
client_credentials_manager = SpotifyClientCredentials(
    client_id='61dcb7d7bff442e3a54a3340825ade72',
    client_secret='ee316ec4c1e848078d9131c8922a343d'
)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def download_audio(url):
    response = requests.get(url)
    
    # save the audio file to disk
    filename = f"{url.split('=')[1]}.mp3"
    with open(filename, "wb") as f:
        f.write(response.content)

    return filename


@Client.on_message(filters.text)
async def get_song_details(client, message):
    song_name = message.text
    results = sp.search(q=song_name, limit=1)
    if results:
        # Send song name
        name = results['tracks']['items'][0]['name']
        
        # Send artist names
        artists = results['tracks']['items'][0]['artists']
        for artist in artists:
            art = artist['name']
        
        # Send album name
        album = results['tracks']['items'][0]['album']['name']
        
        # Get popularity details
        popularity = results['tracks']['items'][0]['popularity']
        
        # Create caption with song details
        caption = f"<b>{name}</b>\n\nArtist: {art}\nAlbum: {album}\nPopularity: {popularity}"
        
        # Send thumbnail image URL
        thumbnail_url = results['tracks']['items'][0]['album']['images'][0]['url']
        await message.reply_photo(thumbnail_url, caption=caption)
        
    else:
        await message.reply_text("Sorry, couldn't find any matching results for that song name.")
        
    try:
        # Send a "searching..." message to inform the user that their request is being processed
        await message.reply("𝖳𝗁𝖾 𝗌𝗈𝗇𝗀 𝗐𝗂𝗅𝗅 𝖻𝖾 𝗎𝗉𝗅𝗈𝖺𝖽𝖾𝖽 𝗂𝗇 @song_requestgroup")

        # Extract the song name from the user's message
        query = message.text

        # Search for the song on Spotify
        result = spotify.search(q=query, limit=1)

        # Extract the URI and name of the song
        uri = result['tracks']['items'][0]['uri']
        name = result['tracks']['items'][0]['name']

        # Get the audio file of the song and upload it to Telegram
        audio_file_url = spotify.track(uri)['preview_url']
        filename = download_audio(audio_file_url)
        with open(filename, "rb") as f:
            await client.send_audio("-1001421860400", f, title=name)

        # Delete the downloaded audio file
        os.remove(filename)

    except Exception as e:
        # Send an error message if something went wrong
        await message.reply(f"Sorry, I encountered an error while processing your request.")
        logging.exception(e)
