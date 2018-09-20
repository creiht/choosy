DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS star;
DROP TABLE IF EXISTS tag;
DROP TABLE IF EXISTS tag_to_star;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE star (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  giffy_id TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES user(id),
  UNIQUE(user_id, giffy_id)
);

CREATE TABLE tag (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE INDEX tag_user_id ON tag(user_id);

CREATE TABLE tag_to_star (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tag_id INTEGER NOT NULL,
  star_id INTEGER NOT NULL,
  FOREIGN KEY(tag_id) REFERENCES tag(id),
  FOREIGN KEY(star_id) REFERENCES star(id)
);

CREATE INDEX tag_to_star_tag_id ON tag_to_star(tag_id);
CREATE INDEX tag_to_star_star_id ON tag_to_star(star_id);
