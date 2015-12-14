# manmonth
**manmonth** helps you to easily get useful and deep information from monitoring your systems with NMON.

**manmonth** is a set of utilities for NMON: Master Assistant NMON To Haven.

Let's supose you want to monitor your system, [NMON](http://nmon.sourceforge.net/pmwiki.php) is an exhaustive and lightweitght to monitor A LOT of your system parameters.

NMON can work 'ala' top, with an interactive console, or you can export NMON output to a file.

For example:
```bash
echo "Monitoring our system in background, snapshot every 10 seconds."
nmon -f -s 10
echo "NMON echoes results to a file with .nmon extension."
```
