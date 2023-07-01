# TempMailCLI

Getting temporary mail address is always good for registering sites anonymously and avoiding spam and tracking.
There is no more geeky way to get temporary mail address then using the terminal.

### Security note: the mail provider will collect some info . for more info, read the user agrement of mail.tm and mail.gw

Requirements:
* requests library
* schedule library
* BeautifulSoup library

service mails:
* mail.tm
* mail.gw

## Use:
## Get repository:
```bash
git repo clone sdebby/TempMailCLI
```

## Install requirements
```bash
cd TemMailCLI
pip install -r requirements.txt
```

## Run
```bash
python tempmailCLI.py
```
You will get a random temporary mail address from mail services.
When new mail arrived, it will be displayed on the terminal.
Press CTRL-C to exit script and delete mail account.
