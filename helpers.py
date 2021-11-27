import functools

def sum_expenses(expenses):
    sum=0
    for key,value in expenses.items():
        sum += value

    return sum

def calculate_stats_for_category(category_expenses):
    # if that list is empty, set total to 0. Otherwise, get the sum
    if category_expenses == []:
        total_category_expenses=0
    else:
        total_category_expenses = functools.reduce(lambda a, b: a+b, category_expenses) 

    category_data={'expense_sum':total_category_expenses,'expense_count':len(category_expenses)}

    return category_data