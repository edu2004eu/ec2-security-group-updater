# ec2-security-group-updater

Small script to automatically update EC2 security group rules
to allow connections to a certain IP. Useful for people with
dynamic IPs.

I've created this script because most I've found were outdated.

I don't care about licensing, so feel free to use this script
however you want.

## Installation

> Note: pipenv is required to be able to follow the instructions.
> If you prefer an alternative (pip, poetry etc.), you will have to
> install the requirements yourself.

1. Clone this repo
2. Run `pipenv install`
3. Give execution permissions to the script: `chmod u+x main.py`
4. Copy `.env.example` to `.env` and set your own values
5. Run the script: `pipenv run python main.py`