#funkcja która zliczy ile razy została wyrzucona dana cyfra kością
#input: int = 56611166626634416
#return -> dict = {'1': 4, '2': 1, '3': 1, '4': 2, '5': 1, '6': 8}

def count_dice(throw):
    dic = {}


    for thr in str(throw):
        if thr in dic:
            dic.update({thr : (dic[thr] +1) })
        else:
            dic.update({thr : 1 })

    dic = dict(sorted(dic.items()))
    

        

    return dic

print(count_dice(56611166626634416))