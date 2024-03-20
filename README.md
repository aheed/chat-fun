# chat-fun

Simple script to use ChatGPT with function calling

Inspired by [YouTube Video](https://www.youtube.com/watch?v=i-oHvHejdsc).

## Installation

Install required packages.
```shell
pip install openai portkey-ai
```
Modify `constants.py.default` to use your own [OpenAI API key](https://platform.openai.com/account/api-keys), and to use you own [Portkey API key](https://app.portkey.ai/). Rename it `constants.py`.

## Example usage
```shell
python main.py
```
### ⚠️
Pay attention to the **"Go ahead?"** questions if this assistant wants to run shell commands on your computer!


## Running inside a docker container
Useful to provide a safe sandbox environment

```shell
docker build -t chat-fun .
docker run -it --rm chat-fun
```

### Mount local directories
To also provide read-only access to your home directory
```shell
docker run -it --rm -v $HOME:/root:ro chat-fun
```

This example also provides read-write access to a directory of your choice, in this example ~/tmp. And gives the container a predictable name.
```shell
docker run -it --rm -v $HOME:/root:ro -v $HOME/tmp:/app/tmp --name chat-fun-container chat-fun
```


