# Ubuntu Installation Documentation

1. Install Python3 and the latest SUMO build 
   
    - Link for installation files [https://sumo.dlr.de/docs/Downloads.php](https://sumo.dlr.de/docs/Downloads.php)
        - Link for linux instructions [https://sumo.dlr.de/docs/Installing/Linux_Build.html](https://sumo.dlr.de/docs/Installing/Linux_Build.html)
        - For Linux additional packages may be needed (including  git). See below before following instructions

            ```
           sudo apt-get install -y openjdk-8-jdk
           sudo apt-get install -y default-jdk
           export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
           sudo apt-get install python-dev
           sudo apt update
           sudo apt upgrade
           sudo apt install git
           sudo apt install python-pip
           pip install setuptools
           ```
          
2. Add this directory's path to the PYTHONPATH environmental variable
    - For reference see [https://bic-berkeley.github.io/psych-214-fall-2016/using_pythonpath.html#if-you-are-on-linux](https://bic-berkeley.github.io/psych-214-fall-2016/using_pythonpath.html#if-you-are-on-linux)

3. Navigate via Terminal or Command Prompt to the US69 directory
4. Create a virtual environment for python. see [https://docs.python-guide.org/dev/virtualenvs/](https://docs.python-guide.org/dev/virtualenvs/)
5. Activate this environment
6. Install the required libraries in this environment by running `pip install -r requirements.txt`
7. In pycharm (or other IDE) open FILENAME_AND_PATH from the project tree and...
