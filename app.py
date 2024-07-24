import gradio as gr
import openai
import config
import pyaudio

openai.api_key =  config.OPENAI_API_KEY
p = pyaudio.PyAudio()

msgs=[
        {"role": "system", "content": "You are a hotel receptionist, your job is to help customers check in to their room. \
        You can only respond when a customer asks you a question. Do not start the conversation. Always wait for a question.\
        The customer does not speak your language, so keep your responses simple and clear."},
    ]
def transcribe(audio):
    global msgs

    media_file = open(audio, "rb")

    # Step 1 - read in the French audio and convert it into English
    translation = openai.audio.translations.create(
        model="whisper-1",
        file=media_file,
    )    
    msgs.append({"role": "user", "content": translation.text})
    if(len(translation.text)>10):
        print(translation.text)

        # Step 2 - use the English text to generate a response
        response2 = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=msgs
        )
        msgs.append({"role": "assistant", "content": response2.choices[0].message.content})
        print("step2: ", msgs)

        # Step 3 - convert the response into French text
        response3 = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                    {
                        "role": "user",
                        "content": "Translate the following text into French: " + response2.choices[0].message.content
                    }
            ] )
        print("step3: ", msgs)
        
        # step 4 - convert the french text to audio and stream the response
        stream = p.open(format=8,
                    channels=1,
                    rate=24_000,
                    output=True)

        with openai.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=response3.choices[0].message.content,
            response_format="pcm"
        ) as response:
            for chunk in response.iter_bytes(1024):
                    stream.write(chunk)

        p.close(stream)

        # step 5 - update the text on the screen
        chat = response3.choices[0].message.content
    else:
        chat = ''
    return chat

# use gradio to create a simple interface 
gr.Interface(
    fn=transcribe,
    live=True,
    inputs=gr.Audio(sources="microphone", type="filepath", streaming=True),
    outputs="text",
).launch()
