import gradio as gr
import openai
import config
import pyttsx3

openai.api_key =  config.OPENAI_API_KEY

messages=[
        {"role": "system", "content": "You are a hotel receptionist, \
                your job is to help customers check in to their room. You can only respond when a customer asks you a question. \ 
                Do not start the conversation wait for a question."},
    ]
def transcribe(audio):
    global messages
    media_file = open(audio, "rb")
    transcription = openai.audio.transcriptions.create(
    model="whisper-1",
    file=media_file,
    )    
    messages.append({"role": "user", "content": transcription.text})
    print(messages)
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    AImessage = response.choices[0].message.content
    engine = pyttsx3.init()
    engine.say(AImessage)
    engine.runAndWait()
    messages.append({"role": "assistant", "content": AImessage})
    chat = ''
    for message in messages:
        if message["role"] != 'system':
            chat += message["role"] + ':' + message["content"] + "\n\n"
    print(chat)
    return chat

gr.Interface(
    fn=transcribe,
    live=True,
    inputs=gr.Audio(sources="microphone", type="filepath", streaming=True),
    outputs="text",
).launch()
