# NBA Analysis Platform

#### Goals:
- Making it intuitive to fetch NBA data.
- Creating up-to-date advanced analytics.
- Giving predictions for upcoming matches.

## Examples:
```python
from nba_analysis import NBAPlayer
from nba_analysis.plotters import plot_scatter_shots, plot_hex_shots, plot_fgp_range_curve
```

### Get a List of All Players


```python
players = NBAPlayer.get_players_list(is_active=True)
```

### Fetch the Player Wanted


```python
jh = players['James Harden']
```

### Get shot stats (Made and Missed Field Goals)


```python
jh_shots = jh.get_shot_details(made_miss=False)
missed = jh_shots[jh_shots.SHOT_MADE_FLAG == 0]
made = jh_shots[jh_shots.SHOT_MADE_FLAG == 1]
```

### Plots density of Field Goal Attemps per Location


```python
ax = plot_hex_shots(jh_shots.LOC_X, jh_shots.LOC_Y)
```


![png](https://user-images.githubusercontent.com/34514167/72778569-518e8400-3be7-11ea-855a-a07ed3db0f65.png)


### Plots density of Field Goal Makes per Location


```python
ax = plot_hex_shots(made.LOC_X, made.LOC_Y)
```


![png](https://user-images.githubusercontent.com/34514167/72778596-63702700-3be7-11ea-921f-413097fdde5b.png)


### Plots density of Field Goal Misses per Location


```python
ax = plot_hex_shots(missed.LOC_X, missed.LOC_Y)
```


![png](https://user-images.githubusercontent.com/34514167/72778606-6b2fcb80-3be7-11ea-94c8-b1d271314cd6.png)

### Scatter Plot for All Shot Attempts (Made : Green, Missed: Red)


```python
ax = plot_scatter_shots(made.LOC_X, made.LOC_Y, missed.LOC_X, missed.LOC_Y)
```


![png](https://user-images.githubusercontent.com/34514167/72778607-6b2fcb80-3be7-11ea-8815-793ab00d24c6.png)



### Plotting Field Goal Percentage vs. Range Curve


```python
ax = plot_fgp_range_curve(jh_shots.SHOT_DISTANCE, jh_shots.SHOT_MADE_FLAG)
```


![png](https://user-images.githubusercontent.com/34514167/72778608-6bc86200-3be7-11ea-9489-6e3f7d228df8.png)
