# Blum-v2 

AUTO CLAIM FOR BLUM / @blum

[![Join our Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/tgairdroptrick)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/man296)

# Table of Contents
- [BlumCum](#blum-v2)
- [Warning](#warning)
- [Available Features](#available-features)
- [Registration](#registration)
- [How to Use](#how-to-use)
  - [About Proxies](#about-proxies)
  - [Termux](#termux)
- [Viewing Reports](#viewing-reports)
- [Thank You](#thank-you)



# Warning

All risks are borne by the user

# Available Features

- [x] Automatic Claim Every 8 Hours
- [x] Automatic Daily Check-In (Login)
- [x] Automatic Claim of Referral Results
- [x] Proxy Support
- [x] Automatic Task Completion
- [x] Automatic Game Play after Claiming
- [x] Multi-process support
- [x] Random User-Agent
- [x] Total balance report of all accounts
- [x] Waiting time before starting the program

# Registration

Click the following link to register: [https://t.me/BlumCryptoBot/](https://t.me/blum/app?startapp=ref_8xXVREQ6fD)

# How to Use

## About Proxies


You can add proxy lists in the `proxies.txt` file, and the proxy format is as follows:

If there is authentication:

Format:

```
protocol://user:password@hostname:port
```

Example:

```
http://admin:admin@69.69.69.69:6969
```

If there is no authentication:

Format:

```
protocol://hostname:port
```

Example:

```
http://69.69.69.69:6969
```

Please pay close attention to whether the proxy you are using requires authentication or not, as many people DM me asking about how to use proxies.


## Termux

1. Make sure your device has Python and Git installed.

    Recommendation: Use Python version 3.8+ (3.8 or newer)
   
   Python
   ```shell
   pkg install python3
   ```
   Git
   ```shell
   pkg install git
   ```

2. Clone this repository.
   ```shell
   git clone https://github.com/man296/blum-v2.git
   ```

3. Enter the BlumCum folder
   ```
   cd BlumCum
   ```

4. Install the required modules/libraries.
   ```
   python -m pip install -r requirements.txt
   ```

5. Edit the `data.txt` file, enter your query data into the `data.txt` file. One line for 1 account, if you want to add a 2nd account, fill it in on a new line.

6. Run the program/script.
   ```
   python bot.py
   ```

## How to get tgWebAppData (query_id / user_id)

1. Login telegram via portable or web version
2. Launch the bot
3. Press `F12` on the keyboard 
4. Open console
5. Сopy this code in Console for getting tgWebAppData (user= / query=):

```javascript
copy(Telegram.WebApp.initData)
```

6. you will get data that looks like this

```
query_id=AA....
user=%7B%22id%....
```
7. add it to `data.txt` file or create it if you dont have one


You can add more and run the accounts in turn by entering a query id in new line like this:
```txt
query_id=xxxxxxxxx-Rxxxxujhash=cxxx
query_id=xxxxxxxxx-Rxxxxujhash=cxxxx
```

## This bot helpfull?  Please support me by buying me a coffee: 
``` 0x9feefCA42b358605f01Ad3A9A7453D57a0d6f42e ``` - BSC (BEP 20)

``` UQCRZj5hG8CrWOQEOLdMex3VGcR6SDABBNnxBMmBscTpBunT ``` - TON

``` bc1qjeuyav3sn2ryph4ag9fa5nshtxtkgau0q0vs43 ``` - BTC (NATIVE SEGWIT)

## Contact
For questions or support, please contact [me](https://t.me/bukaneman)

# Thank You
