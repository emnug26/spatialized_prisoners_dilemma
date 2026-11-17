possible_strategies:
    Strategy(False, False, False),  #allways defect             black
    Strategy(False, False, True),   #suspicious_doormat         blue
    Strategy(False, True, False),   #suspicious_TFT             green
    Strategy(False, True, True),    #suspicious_pacifist        cyan
    Strategy(True, False, False),   #deceptive_defector         red
    Strategy(True, False, True),    #guillible_doormat          magenta
    Strategy(True, True, False),    #regular_TFT                yellow
    Strategy(True, True, True)      #regular_pacifist           white

With the default rewards regular_TFT will almost always win in a sufficiently large grid. (tested at 64*64)
