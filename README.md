# Clippy
Giving the power of AI to everyone's favorite paperclip

<img width="250" alt="image" src="https://user-images.githubusercontent.com/69104218/223997198-b82ea145-8d21-4534-97e4-fc4d65a8a711.png">

## What can it do
It answers questions using the GPT3 API, work is being done to migrate it to the new ChatGPT API

## How do I use it?
1. `git clone https://github.com/Bluebotlaboratories/Clippy`
2. `pip3 install -r requirements.txt`
3. Add your OpenAI API key to the `secrets.json` file
4. If you want Clippy to remember history at the cost of tokens, change the `useMemory` in `models.py`
5. Run `python main.py`
6. "Enjoy"
