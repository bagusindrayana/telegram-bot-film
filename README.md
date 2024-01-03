## Bot Telegram
Bot Telegram untuk mencari link stream film dari PusatFilm melalui api https://perompak7samudra.vercel.app

## Cara Install
- Clone repository ini
- `pip install -r requirements.txt`
- buat database postgresql
- buat table `history_film`
  ```sql
    CREATE TABLE history_film (
        id serial PRIMARY KEY,
        message_id varchar(255) NOT NULL,
        link varchar(255) NOT NULL,
        created_at timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    ```
- copy file `.env.example` menjadi `.env` dan isi token bot telegram dan informasi databasenya
- jalankan `python main.py`

## Deploy
- ubah `ENV` pada `.env` menjadi `production`
- tambahkan url web ke `WEBHOOK_URL` pada `.env`
- buka webnya, kemudian cek status webhook pada route `/status`

## Demo Bot
- https://t.me/PusatFilmBot