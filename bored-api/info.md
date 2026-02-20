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

### GitHub Actions Endpoints

These endpoints will be reached out to by github actions, initiating the process.

#### /review

Messaged when review is started

#### /merge

Messaged when two branches are merged

#### /pr

Messaged when a pull request is made

#### /branch

Messaged on branch creation

### /checkout

This endpoint will be reached out to by the code plugin to indicate that they have checked out a branch, giving them the new todo list.

### /confirm

This endpoints will be reached out to by the Code plugin to get and confirm changes. A header argument **"session-id"** should be passed which contains the session for which the changes are to be made. Posting to this endpoint writes passed changes to board, getting it recives possible changes.

### /init

This endpoint is for creating a new session. Can pass **"session-id"** string to use a specific session ID or can get assigned one. The new session will have no tasks, they will have to be passed later.

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