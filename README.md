# Toybus Discord Bot

A Discord Bot

## Prerequisites

Ensure that Python 3.10 is installed on your system.

## Installing Dependencies

Dependencies are listed in the `requirements.txt` file. You can install them using pip by running the following command:

```bash
$ pip install -r requirements.txt
```

Alternatively, if you prefer using Pipenv for managing project dependencies, you can install them with:

```bash
$ pipenv install
```

This will create a virtual environment and install all the required packages as specified.

## Setting up Environment Variables

You need to set up environment variables to store sensitive information such as your bot's token. Create a `.env` file in the root directory of the project and add the following line:

```.env
BOT_TOKEN=<YOUR_TOKEN>
```

Replace `<YOUR_TOKEN>` with your actual Discord bot token. This file should not be shared or committed to version control systems for security reasons.

## Running the Project

To start the Bot, run the following command:

```bash
$ python3 main.py start
```

To stop the Bot, run the following command:

```bash
$ python3 main.py stop
```
