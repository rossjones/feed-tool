#!/usr/bin/env python

import os
import sys
import json
import sqlite3
import datetime
import scraperwiki
import feedparser
import argparse


def write_response(r=None, success=True, message=None):
    d = {
        "results": r,
        "success": "ok" if success else "error",
        "message": message or ""
    }
    json.dump(d, sys.stdout)
    sys.stdout.flush()


class Feed(object):

    @classmethod
    def retrieve(cls, name, url):
        try:
            d = feedparser.parse(url)

            # Check it is actually a feed
        except Exception as e:
            return None, None

        name = name or d['feed'].get('title', 'subtitle')
        for e in d.entries:
            r = {
                "feed": name,
                "source": url,
                "id": e.id,
                "title": e.title,
                "link": e.link,
                "published": e.link,
                "updated": e.updated,
                "summary": e.summary,
                "content": e.content if hasattr(e, "content") else "",
            }        
            scraperwiki.sqlite.save(["id","link"], r, "entries")

        return name, None

class FeedManager(object):

    def status(self):
        """
        Returns the current status of the feeds as a list of dicts where
        each dict contains:
            name, url, count of entries, last_fetch, last_error
        """
        res = []
        rows = scraperwiki.sqlite.execute("select name,url from feeds")
        for row in rows['data']:
            nm = row[0]
            url = row[1]
            cnt = scraperwiki.sqlite.execute("select count(*) from entries where feed=? and source=?", [nm, url])
            cnt = int(cnt['data'][0][0])
            d = {
                "name": row[0],
                "url" : row[1],
                "items": cnt
            }
            res.append(d)

        write_response(res)


    def add(self, url):
        """
        Adds a new feed when provided with a URL, if successful returns the
        status()
        """
        name, err = Feed.retrieve(None, url)
        if err:
            write_response(success=False, message=err)
            return

        f = {
            "name": name,
            "url": url
        }
        scraperwiki.sqlite.save(['name', 'url'], f, "feeds")
        self.status()


    def remove(self, url):
        """
        Removes an existing feed when provided with a URL, if successful returns the
        status()
        """    
        scraperwiki.sqlite.execute("delete from feeds where url='%s';" % url)
        scraperwiki.sqlite.commit()
        self.status()

    def reset(self):
        """
        Removes all data :(
        """
        scraperwiki.sqlite.execute("delete from feeds")
        scraperwiki.sqlite.execute("delete from entries")
        self.status()

    def process(self):
        """
        Iterates through all of the feeds and fetches the contents, before writing
        them to the database.
        """
        feeds = scraperwiki.sqlite.execute("select name,url from feeds")
        for nm,url in feeds['data']:
            Feed.retrieve(nm, url)

        self.status()


# Make sure the database exists, setting up the entries and feeds table.
scraperwiki.sql.dt.create_table({'id': '1'}, 'entries')
scraperwiki.sql.dt.create_table({'name':'', 'url': ''}, 'feeds')

# Read command line args to decide what we should be doing
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--status', action='store_true')
parser.add_argument('--reset', action='store_true')
parser.add_argument('--add', action='store')
parser.add_argument('--remove', action='store')
parser.add_argument('--process', action='store_true')

feeder = FeedManager()

args = parser.parse_args()
if args.status:
    feeder.status()
elif args.add:
    feeder.add(args.add)
elif args.remove:
    feeder.remove(args.remove)
elif args.reset:
    feeder.reset()
elif args.process:
    feeder.process()
