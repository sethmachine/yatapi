# yatapi

![Yatapi Usage Demo](img/yatapi-usage.gif "Yatapi Usage")

Yet Another Trigger API (YATAPI) is a Python based generator of SCMDraft TrigEdit triggers featuring **type annotations**, **autocompletion** (with a Python IDE) **one-to-one correspondence with TrigEdit triggers**, and **object oriented programming design**.  YATAPI is designed to work with [PyCharm](https://www.jetbrains.com/pycharm/download/#section=mac), a modern Python IDE, and requires only basic Python scripting knowledge and how Starcraft Triggers work.  YATAPI is **minimalist** and **extensible**, and can be used as the base for more advanced triggering.  Since YATAPI is a **whitebox**--it has a one-to-one correspondence with Starcraft Triggers, there is no need to learn a new specialized triggering language or framework.  

## Comparison
There are numerous other tools, frameworks, and projects aiming to make triggering automatable and easier.  YATAPI was created after reviewing these and determining they did not meet the need of the author.  Poor documentation and/or lack of examples were also criteria.  YATAPI is not meant to replace frameworks but rather serve as a base for others to build more advanced trigger systems.  See this [staredit.net discussion](http://www.staredit.net/topic/17706/#2) for what prompted me to create YATAPI.  

| Feature                               | YATAPI             | LangUMS            |
|---------------------------------------|--------------------|--------------------|
| Python                                | :white_check_mark: | :x:                |
| Smart Autocompletion                  | :white_check_mark: | :question:         |
| Type Annotations                      | :white_check_mark: | :question:         |
| PyCharm IDE                           | :white_check_mark: | :x:                |
| One-to-one correspondence to triggers | :white_check_mark: | :x:                |
| Install with pip                      | :white_check_mark: | :x:                |
| Active Project                        | :white_check_mark: | :question:         |
| Examples                              | :white_check_mark: | :white_check_mark: |
| Easy to Extend                        | :white_check_mark: | :x:                |






## Requirements

### System Requirements

* Python 3.6.x.  Recommended to use [miniconda](https://docs.conda.io/en/latest/miniconda.html) to manage Python virtual environments or similar tools.  miniconda will also install Python if not already on your system.
* [PyCharm IDE](https://www.jetbrains.com/pycharm/download/).  PyCharm community edition is available for free and takes full advantage of YATAPI's type annotations for creating easy to verify triggers.  
* [SCMDraft 2.0](http://www.stormcoast-fortress.net/cntt/software/scmdraft/download/).  This version has TrigEdit built in, which allows for creating triggers via text.

### Technical Requirements

* Basic command line usage familiarity (macOS Terminal or Windows command prompt)
* [Basic knowledge of Python scripting](https://www.python.org/about/gettingstarted/).  
* Knowledge of how Starcraft triggers work (i.e. you have made a custom map before).
* Understanding the difference between [value and reference semantics](https://stackoverflow.com/questions/373419/whats-the-difference-between-passing-by-reference-vs-passing-by-value)


## Installation

This assumes your system has met all [Technical Requirements](#technical-requirements).


![Install YATAPI Demo](img/install-yatapi-gif.gif "Install Yatapi Demo")

1.  Clone or download this repository to your local machine, e.g. run `git clone https://github.com/sethmachine/yatapi.git` in your terminal or use the "Download Zip" option if you do not have a git client installed.

2.  (optional) Create and activate a Python virtual environment for your project:
    * With miniconda: `conda create --name my-project python=3.6`
    * Activate before installing: `source activate my-project`.  On Windows use `activate my-project`.  

3.  Install YATAPI using `pip` (included with modern Python installations):
    ```bash
    # assuming you cloned yatapi to your desktop
    $ cd ~/desktop/yatapi
    # (optional) use a virtual environment you created in step 2 before installing
    # note use `activate my-project` if using Windows
    # this will prepend the virtual environment name to the terminal prompt
    $ source activate my-project
    (my-project) $ pip install src/
    ```

4.  Verify YATAPI is installed: `python -c "import yatapi; print(yatap.__file__);"`.  Output should look like this: "/Users/sethmachine/miniconda3/envs/yatapi-examples/lib/python3.6/site-packages/yatapi/\_\_init\_\_.py".  If there is an error, the output will look like this: "ModuleNotFoundError: No module named 'yatapi'".  

## Usage

See the scripts in the [examples folder](https://github.com/sethmachine/yatapi/tree/master/examples), especially [war\_in\_north\_hero\_revive.py](https://github.com/sethmachine/yatapi/blob/master/examples/war_in_north_hero_revive.py) for a fully detailed example.

The core constructs are `Condition`, `Action`, and `Trigger` objects.  Each trigger object is made up of a list of `SCPlayer` objects (the players or forces for which the trigger executes) and a corresponding list of conditions and actions.  This is exactly how triggers are written in Campaign Editor GUI.  

## Contribute

Contributors are very welcome.  Clone the project and create your own branch to test out your additions or changes.  Create test cases and then make a pull request describing what you added or change.  I will review any requests or issues at least once a day.  Please review the key tenet of YATAPI before considering a change:

YATAPI is **minimalist**, and does not feature anything that cannot be accomplished with vanilla triggers.  Features like Death Counter Management should be done in codebases that build on YATAPI's API and not in YATAPI itself.  

## FAQ

### Does YATAPI check for any compilation or syntax errors?

Currently, no (but a very good idea).  The best way to check actual errors will be when copy and pasting to SCMDraft and seeing the TrigEdit complain about certain lines.  YATAPI will also happily compile triggers with more than 64 actions or conditions (but this kind of check could be easily added in).  

### How does YATAPI handle death counters?

YATAPI is minimalist and does not have any logic for death counter management.  These would be created using the `Deaths` and `SetDeaths` trigger statements.  On the other hand, motivated mappers are welcome to build ontop of YATAPI to create more advanced scripting of triggers, including death counter management systems.  The besy way would be to create a new Python project that has YATAPI as a requirement in the requirements.txt or setup.py.  

### YATAPI is missing X action or condition

YATAPI was built in a semi-automated fashion from TrigEdit output and is missing some actions and conditions.  Any motivated mapper is welcome to contribute to YATAPI by adding the missing actions or conditions and making a pull request.  

