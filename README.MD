# Choosy Gifs

This is a basic search engine for giphy gifs.  It is just a fun project to learn some new things and reacquaint myself with some old things :)

It is written using Python 3, Flask, and Material Design Lite.

## Running a Dev Instance

  1. Download this repo.
  2. Install the requirements:
    * `pip3 install -U flask`
    * `pip3 install -U giphy_client`
    * `pip3 install -U pytest` (For testing)
  3. Initialize the DB:
    * `./init_db.sh`
  4. Run the flask server with the Choosy app:
    * `./run.sh`
  5. Browse to http://localhost:5000/
  6. Register a user and have fun!

## Future improvements

  1. Mock out the giphy api calls so that we can have better test coverage.
  2. Add proper DB support (currently uses SQLite with a light DB abstraction).
  3. Add caching layer (Redis or similar) for session information and caching api calls.
  4. Explore JS Frameworks to add a more dynamic app experience.
  5. Improve tag management.

