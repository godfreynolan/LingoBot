import gradio as gr
import openai
import config
from playsound import playsound

openai.api_key =  config.OPENAI_API_KEY
speech_file = "french.mp3"

messages=[
        {"role": "system", "content": "You are a hotel receptionist, your job is to help customers check in to their room. \
        You can only respond when a customer asks you a question. Do not start the conversation wait for a question.\
        The customer does not speak your language, so keep your responses simple and clear."},
    ]
def transcribe(audio):
    global messages
    media_file = open(audio, "rb")

    # Step 1 - read in the French audio and convert it into English
    translation = openai.audio.translations.create(
        model="whisper-1",
        file=media_file,
    )    
    messages.append({"role": "user", "content": translation.text})

    # Step 2 - use the English text to generate a response
    response2 = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    messages.append({"role": "assistant", "content": response2.choices[0].message.content})

   # Step 3 - convert the response into French text
    response3 = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {
                    "role": "user",
                    "content": "Translate the following text into French: " + response2.choices[0].message.content
                }
        ] )
        
    # step 4 - save the French text as an audio file
    with openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="nova",
        input=response3.choices[0].message.content
    ) as response:
        response.stream_to_file(speech_file)

    # step 5 - play the audio file
    chat = response3.choices[0].message.content
    playsound(speech_file)
    return chat

gr.Interface(
    fn=transcribe,
    live=True,
    inputs=gr.Audio(sources="microphone", type="filepath", streaming=True),
    outputs="text",
).launch()
