# deutsche-bahn-time-display

A small Python script to display and refresh periodically the time of your next train(s) in a terminal.

Since it is fetching data from the Deutsche Bahn, you may use this script for display next connection times on any line in whole germany. It takes into account delays, train cancelations, and probably missed connections on the way. 

When a delay information is available, the number of minutes `Y` is added to the display time `Z`` as `Z+Y`. If other troubles are detected (train canceled, connection will be probably missed), the character `X` is displayed besides the number of minutes `Z` as `ZX`. In that case, it is better to check manually online for more information. 

## Example

I use this micro app to display on the screen of my raspberry pi the time for the next trains leading the places in am interested to. For example, when it is 13:41, it would display something like this for my places of interest `P1`, `P2` and `P3`:

```
=========================
=P1===> 01, next in 09,11
 13:42 | 13:50 | 13:52

=P2==> 29, next in 59,74
 14:10 | 14:40 | 14:55

=P3=> 08, next in 28,48
 13:50 | 14:10 | 14:30
.........................
```

## About

The script uses [schiene](https://github.com/kennell/schiene), a cool Python library for interacting with Bahn.de (as an unofficial API client). You may need to install it beforehand. 

```
pip install schiene
```

