# betfair-bookrunner

Sportsbook betting robot for Betfair.com

The robot is capable of collecting sportsbook market information,
recording individual markets and odds movements during the duration of events.

The robot is driven by a configurable strategy.

## Running Application

Display help:

```
./bin/run.sh --help
```

Run application in data collection mode

```
./bin/run.sh
```

Run application with live betting and data collection

```
./bin/run.sh --account BETFAIR_ACCOUNT_NAME
```

## Strategy

Betting strategy defined in JSON format

```
cat ./app/config/default.json
```

## Backtesting

Verify sportsbook event information is recorded

```
ls ~/.bookrunner/backtest/
```

Example recording file

```
cat ~/.bookrunner/backtest/soccer_924.242082168_match_odds
```

Format: GAME_TIME, EVENT_NAME, SCORE, ODDS_HOME, ODDS_DRAW, ODDS_AWAY

> 2,Etimesgut Belediyespor v Elazigspor,0-0,2.4,2.9,2.8
>
> 2,Etimesgut Belediyespor v Elazigspor,0-0,2.4,2.8,2.8
>
> 2,Etimesgut Belediyespor v Elazigspor,0-0,2.4,2.9,2.8
>
> 4,Etimesgut Belediyespor v Elazigspor,0-0,2.4,3.0,2.7
>
> 4,Etimesgut Belediyespor v Elazigspor,0-0,2.5,2.8,2.7
>
> 4,Etimesgut Belediyespor v Elazigspor,0-0,2.5,2.8,2.7

Code your own backtesting logic, run example included file:

```
./backtest/soccer_match_odds_hedge.py
```

> SPORT - soccer - MARKET - match_odds
>
> BALANCE - 88.89 - PROFIT - -10.96
>
> LOW - 87.37 - HIGH - 102.72
>
> TOTAL MARKETS - 409
>
> TOTAL BETS - 0 - BETS WON - 98 - BETS LOST - 140
>
> TOTAL STAKE - 168.73 - TOTAL RETURN - 157.77
