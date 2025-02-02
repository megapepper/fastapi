create table if not exists user_app (
    id serial primary key, 
    name text constraint namechk check(char_length(name)<=50),
    avatar_url text constraint avatar_urlchk check(char_length(avatar_url)<=255)
);
create table if not exists user_credential (
    user_id integer REFERENCES user_app, 
    login text unique constraint loginchk check(char_length(login)<=50), 
    password text constraint passwchk check(char_length(password)<=255), 
    salt text constraint saltchk check(char_length(salt)<=255)
);


