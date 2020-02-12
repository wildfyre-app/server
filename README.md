# WildFyre Server

## Setup without an IDE, or with Visual Studio

Instructions for Unix, Windows, with or without Visual Studio, can be found [on our Phabricator wiki](https://phabricator.wildfyre.net/w/api/set_up/).

## Setup in PyCharm

 - Open the project (PyCharm should recognize it thanks to the .idea directory)
 - Create a new interpreter:
    - File → Settings → Project → Project Interpreter
    - Tap the cog icon in the top-right → add
    - Select 'virtual environment', 'new', set its path to `api/venv` in the project's root. Name the environment "Python (WildFyre Server)". Ensure at least Python 3.6 is used.
 - Enable Django support: File → Settings → Language & Frameworks → Django
    - Tick 'enable support'
    - The project root is the 'api' directory
    - The settings file is 'api/settings.py'
    - The manage is 'manage.py'

 - Run the following commands:

```bash
$ cd api/
$ chmod u+x venv/bin/activate
$ source venv/bin/activate
$ pip install -r requirements.txt
```

To initialize the project:
 - Run the configuration "Migrate"
 - Run the configuration "Create superuser". Follow the prompts to create the admin user.

The configuration 'Run server' runs the server on http://localhost:8000.

The configuration 'Tests' runs unit tests.