# Bored API

The bored API will be called when the following actions are taken with the following information granted. All requests will have a token related to the project it is for as well.

## Structure and Requirements

* On Review
    * Branch Title
    * Diff
* On Merge
    * Branch Title
    * Diff
* On PR
    * Branch Title
    * Diff
* On Branch Creation
    * Branch Title
    * Branch From

## Endpoints

### /review

Messaged when review is started

### /merge

Messaged when two branches are merged

### /pr

Messaged when a pull request is made

### /branch

Messaged on branch creation

### /admin/serverupdate

Messaged to update the server remotely. When messaged, needs the **"admin-key"** to be passed in the header.

## Setup

### Python Virtual Environment

Linux

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate && pip install -r requirements.txt
```

### Setting Passwords on Server

Create /bored-api/.env and add the following, replacing the password fields with secure passwords and keys

```text
admin-key: <key>
path: <pathtorepo>
```