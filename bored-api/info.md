# Bored API

The bored API will be called when the following actions are taken with the following information granted. All requests will have a token related to the project it is for as well.

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