import requests

def fail_stack_buy_value(cry=True, region="sea"):
    url = f'https://api.arsha.io/v2/{region}/item?id=44195,16001,16004,721003,4998,8411,44364,4918,65319,820979,820934,767102&lang=en'
    response = requests.get(url)
    
    misc_price = {}
    for item in response.json():
        misc_price[item['name']] = item['lastSoldPrice']
    misc_price['Mass of Pure Magic'] = 500000

    fail_stack_buy_value = [0] * 314
    fail_stack_buy_value[1] = misc_price['Black Stone']
    fail_stack_buy_value[5] = misc_price['Black Stone'] * 5
    fail_stack_buy_value[10] = misc_price['Black Stone'] * 12
    fail_stack_buy_value[15] = misc_price['Black Stone'] * 21
    fail_stack_buy_value[20] = min(misc_price['Black Stone'] * 33, misc_price['Dragon Scale Fossil'] * 20)
    fail_stack_buy_value[25] = misc_price['Black Stone'] * 53
    fail_stack_buy_value[30] = min(misc_price['Black Stone'] * 84, misc_price['Dragon Scale Fossil'] * 50)
    fail_stack_buy_value[35] = misc_price['Black Stone'] * 136
    fail_stack_buy_value[40] = min(misc_price['Black Stone'] * 230, misc_price['Dragon Scale Fossil'] * 150)
    fail_stack_buy_value[45] = misc_price['Black Stone'] * 406
    fail_stack_buy_value[50] = min(misc_price['Crystallized Despair'] * 4, misc_price['Dragon Scale Fossil'] * 400)
    fail_stack_buy_value[60] = misc_price['Crystallized Despair'] * 8
    fail_stack_buy_value[70] = misc_price['Crystallized Despair'] * 15
    fail_stack_buy_value[80] = misc_price['Crystallized Despair'] * 25
    fail_stack_buy_value[90] = misc_price['Crystallized Despair'] * 35
    fail_stack_buy_value[100] = misc_price['Crystallized Despair'] * 50

    blank_values = []
    old_fs = 1
    for fs in range(2, 101):
        if fail_stack_buy_value[fs]:
            increase = (fail_stack_buy_value[fs] - fail_stack_buy_value[old_fs]) / (fs - old_fs)
            for val in blank_values:
                fail_stack_buy_value[val] = increase * (val - old_fs) + fail_stack_buy_value[old_fs]
            blank_values = []
            old_fs = fs
        else:
            blank_values.append(fs)

    def dark_origin(fs):
        dark_list = [
            [102, 26], [106, 25], [109, 24], [112, 23], [116, 22], [120, 21], [125, 20], [130, 19],
            [136, 18], [142, 17], [149, 16], [157, 15], [166, 14], [176, 13], [188, 12], [197, 11],
            [207, 10], [218, 9], [236, 8], [255, 7], [270, 6], [292, 5], [297, 4], [298, 3], [299, 2], [300, 1]
        ]
        for a in dark_list:
            if fs < 100:
                return 0
            elif fs < a[0]:
                return a[1]
        return 0

    def faint(fs):
        faint_list = [
            [105, 13], [110, 12], [118, 11], [125, 10], [135, 9], [147, 8], [164, 7], [180, 6],
            [206, 5], [229, 4], [268, 3], [299, 2], [300, 1]
        ]
        for a in faint_list:
            if fs < 100:
                return 0
            elif fs < a[0]:
                return a[1]
        return 0

    for fs in range(100, 300):
        do = dark_origin(fs)
        price = misc_price['Origin of Dark Hunger'] / do if do else 0
        for n in range(do):
            if fail_stack_buy_value[fs+n+1]:
                fail_stack_buy_value[fs+n+1] = min(fail_stack_buy_value[fs+n+1], fail_stack_buy_value[fs+n] + price)
            else:
                fail_stack_buy_value[fs+n+1] = fail_stack_buy_value[fs+n] + price
        fdo = faint(fs)
        if fdo:
            price = misc_price['Faint Origin of Dark Hunger'] / fdo
            for n in range(fdo):
                if fail_stack_buy_value[fs+n+1]:
                    fail_stack_buy_value[fs+n+1] = min(fail_stack_buy_value[fs+n+1], fail_stack_buy_value[fs+n] + price)
                else:
                    fail_stack_buy_value[fs+n+1] = fail_stack_buy_value[fs+n] + price

    if cry:
        for fs in range(304, 0, -1):
            for plus in range(1, 14):
                if fail_stack_buy_value[fs] != 0 and fail_stack_buy_value[fs+plus] != 0:
                    fail_stack_buy_value[fs+plus] = min(fail_stack_buy_value[fs] + 6555891 * plus, fail_stack_buy_value[fs+plus])
                elif fail_stack_buy_value[fs] != 0:
                    fail_stack_buy_value[fs+plus] = fail_stack_buy_value[fs] + 6555891 * plus

    return fail_stack_buy_value
