create table auths (team_id VARCHAR, bot_token VARCHAR, constraint auths_pk primary key (team_id, bot_token));
create table news (id INTEGER primary key autoincrement, title TEXT, summary TEXT, keywords TEXT, url TEXT);
