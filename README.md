#Usage

All responses are wrapped in ...

    {
        "results": r,
        "success": "ok" or "error"
        "message": error_message or ""
    }


### feed.py --status
Returns a list of dicts that look like:

    {
        "name": "feed name",
        "url" : "feed url",
        "items": 100
    }
    
### feed.py --reset
Deletes everything and returns the same as status (will be empty)

### feed.py --add <url to a feed>
Adds a new feed, fetches it and then returns the same as status

### feed.py --remove <url to remove>
Removes the specified feed and returns the status

### feed.py --process
Calls all of the feeds and collects data
