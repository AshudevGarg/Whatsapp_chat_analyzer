import re
import pandas as pd


def preprocess(data):

    # Remove invisible unicode chars (important for iPhone exports)
    data = data.replace('\u200e', '')
    data = data.replace('\u202f', ' ')
    data = data.replace('\xa0', ' ')

    # Android format (supports 24hr + AM/PM)
    android_pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}(?::\d{2})?\s?(?:[APMapm]{2})?)\s-\s'

    # iPhone format
    iphone_pattern = r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2}\s?(?:[APMapm]{2})?)\]'

    # Detect format
    if re.search(iphone_pattern, data):
        pattern = iphone_pattern
    else:
        pattern = android_pattern

    # Split messages
    messages = re.split(pattern, data)[1:]

    dates = []
    users = []
    msgs = []

    i = 0

    while i < len(messages):

        date = messages[i]
        time = messages[i + 1]
        message_block = messages[i + 2]

        i += 3

        full_datetime = date + " " + time

        entry = message_block.strip()

        # Extract user and message
        if ': ' in entry:
            user, message = entry.split(': ', 1)
        else:
            user = 'group_notification'
            message = entry

        dates.append(full_datetime)
        users.append(user)
        msgs.append(message)

    # Create dataframe
    df = pd.DataFrame({
        'user': users,
        'message': msgs,
        'date': dates
    })

    # Convert datetime
    df['date'] = pd.to_datetime(
        df['date'],
        format='mixed',
        dayfirst=True,
        errors='coerce'
    )

    # Remove invalid dates
    df = df.dropna(subset=['date'])

    # Date features
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Extra features
    df['only_date'] = df['date'].dt.date

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    # Remove omitted media lines
    df['message'] = df['message'].fillna('').astype(str)

    df = df[~df['message'].str.contains('omitted', na=False)]

    return df