import re
import pandas as pd

def preprocess(data):

    #Fix weird unicode spaces
    data = data.replace('\u202f', ' ').replace('\u00a0', ' ')

    lines = data.split('\n')

    dates = []
    users = []
    messages = []

    #UNIVERSAL PATTERN (handles both 24-hour & AM/PM)
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\s?[APMapm]{2})?)\s-\s'

    current_message = ""
    current_user = None
    current_date = None

    for line in lines:
        match = re.match(pattern, line)

        if match:
            # Save previous message
            if current_message:
                dates.append(current_date)
                users.append(current_user)
                messages.append(current_message.strip())

            date_part = match.group(1)
            rest = line[len(match.group(0)):]

            current_date = date_part

            if ": " in rest:
                current_user, current_message = rest.split(": ", 1)
            else:
                current_user = "group_notification"
                current_message = rest

        else:
            # Multiline message handling
            current_message += " " + line

    # Add last message
    if current_message:
        dates.append(current_date)
        users.append(current_user)
        messages.append(current_message.strip())

    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'user': users,
        'message': messages
    })

    #Smart datetime parsing (AUTO handles both formats)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Drop invalid rows
    df.dropna(subset=['date'], inplace=True)

    # FEATURES 
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Optional: period (for heatmap)
    df['period'] = df['hour'].apply(
        lambda x: f"{x}-{x+1}" if x != 23 else "23-00"
    )

    return df