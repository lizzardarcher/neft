def get_days_in_month(month, year):
    import calendar
    num_days = calendar.monthrange(year, month)[1]
    return [str(day).zfill(2) for day in range(1, num_days + 1)]

