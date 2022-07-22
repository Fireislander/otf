# otf
A utility for pulling data from your Orange Theory account for better data analysis

* Install `requests` library. `pip3 install requests`
* Update lines 4 and 5 with your OTF email and password
* `python3 main.py`

### This script will currently display
* \# of classes by coach
* Breakdown of class types you have taken
* Your home studio
* \# of classes booked
* \# of classes attended (including those without a HRM)
* \# of intro classes taken
* \# OT Live classes booked
* \# OT Live classes attended
* \# Total classes used HRM
* \# Total studios visited
* \# Max HR (what would show at 100% on the screen)
* Average Max HR across classes
* Average HR across classes
* Average splats
* Average calorie burn
* A min by min breakdown of your average HR
* Average time in each HR zone

The script currently makes a lot of assumptions about what data will be available. Since I only had access to my account I was able to make those assumptions, but some folks had different data that didn't quite match mine, or had data missing. 

Please create an issue on GitHub or [DM me on reddit](https://www.reddit.com/message/compose/?to=/u/fireislander) with any errors/findings/suggestions


### To do (in no particular order):
* Create postman collection to better explore data and make more easily available
* Identify data assumptions and handle errors arising from them
* Pull challenge/benchmark data/progression
* Learn `pandas` for better data processing
* Make pretty graphs
