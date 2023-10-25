# Earnings_Reverse_Boilerplate

- This script aims to provide a backtesting boilerplate for earnings price reversals after 30 days or so.

- I used my backtesting skeleton script and modified that to fit my needs, hence there can be some unnecessary lines of code that can be discarded.

- Thesis is, new earnings can take time for markets to absorb. Thus, there can be reversals after certain period of time post-earnings. Here, I am using 30 days period which at the end we buy/sell closing prices three days in a row depending on the first 30 days' move and close the position after 20ish days


Notes

- Script is a very raw script that doesn't use any parameters but days past. A parameter such as "if price went up significantly in the first 30 days, sell" could improve the performance.

- Portfolio value tracking is a very simple module. I am looking to improve it.

![image](https://github.com/IBatuu/Earnings_Reverse_Boilerplate/assets/78052559/2dfc1d10-1977-4e46-8df2-9d9e6583acd8)
