import re
import pandas as pd


def clean_line(line):
    # Remove 'am' and 'pm' (with or without \u202f)
    cleaned = re.sub(r'\s?\u202f?(am|pm)', '', line.strip())

    # Normalize the year: Change "24" to "2024" and "25" to "2025"
    cleaned = re.sub(r'(\d{1,2}/\d{1,2}/)24', r'\g<1>2024', cleaned)
    cleaned = re.sub(r'(\d{1,2}/\d{1,2}/)25', r'\g<1>2025', cleaned)

    return cleaned


def preprocess(data):
    # Clean the data first
    cleaned_lines = [clean_line(line) for line in data.split("\n")]
    cleaned_data = "\n".join(cleaned_lines)

    # Define pattern for date and time
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
    messages = re.split(pattern, cleaned_data)[1:]
    dates = re.findall(pattern, cleaned_data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert message_date type
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M - ')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []

    for message in df['user_message']:
        entry = re.split(r'([\w\s]+?):\s', message, maxsplit=1)
        if len(entry) > 2:
            users.append(entry[1].strip())
            messages.append(entry[2].strip())
        else:
            users.append('group_notification')
            messages.append(entry[0].strip())

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract additional datetime components
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
