create table auths (
  team_id VARCHAR,
  bot_token VARCHAR,
  constraint auths_pk primary key (team_id, bot_token)
);

create table news (
  id INTEGER primary key autoincrement,
  title TEXT,
  summary TEXT,
  keywords TEXT,
  url TEXT,
  channel_id TEXT,
  user_id TEXT,
  workspace TEXT,
  date TIMESTAMP,
  language TEXT
);

create table categories (
  id INT primary key autoincrement,
  alias TEXT, language TEXT
);

create table categories_news (
	category INT not null
	constraint categories_news_categories_id_fk references categories (id) on delete cascade,
	new INT not null constraint categories_news_news_id_fk references news (id) on delete cascade,
	constraint categories_news_category_new_pk primary key (category, new)
);



