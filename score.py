#file to generate the score for testing the player for their risk of herding behavior
def calc_sp(true_p,mkt_p):
    # sp= percentage difference b/w fake and true market values respectively
    sp=(mkt_p-true_p)/true_p
    return round(sp,2)

# rules to evaluate scores
def evaluate(move,spread):
    # 0.20: (20%) represents dangerous deviation of market value from intrinsic/ true value- a bubble
    # deduct points on buying at bubble
    if(move=="Buy" and spread>0.20):
        return -100
    
    # reward points on selling at bubble
    elif(move=="Sell" and spread>0.20):
        return 100
    
    # partial reward for holding- trying to resist from buying in the bubble
    elif(move=="Hold" and spread>0.20):
        return 50
    
    # reward points on buying outside the bubble
    elif(move=="Buy" and spread<-0.10):
        return 100
    
    # partial reward for taking no action whatsoever
    else:
        return 25

