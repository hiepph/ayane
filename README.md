## Development

+ Python packages:
```sh
$ pip install -r requirements.txt
```

+ Config:
```sh
$ cp config.example.yml config.yml

## config.yml
token # Contact @BotFather for gaining access token
db # Config for Postgresql database
```

+ Database migration:
```
$ psql
# CREATE DATABASE ayaneru
# \c ayaneru
# \i /path/to/ayaneru/sql/migrate.sql
```


## Deploy

+ First start:

```sh
$ python main.py
```

+ Zero downtime deploy:
```
$ git pull origin master
# Chat with @AyaneruBot
> /restart
```
