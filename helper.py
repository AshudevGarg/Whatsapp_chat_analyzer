from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
extract = URLExtract()

def fetch_stats (selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    words=[]
    num_messages=df.shape[0]
    for message in df['message']:
        words.extend(message.split())

    num_media_messages=df[df['message'] == '<Media omitted>' ].shape[0]
    links=[]
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages,len(words),num_media_messages,len(links)

def most_busy_users(df,n):
    x=df['user'].value_counts().head(n)
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'user': 'name', 'count': 'percent'})
    return x,df

def create_word_cloud(selected_user, df):
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = set(f.read().split())
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[
        (df['user'] != 'group_notification') &
        (~df['message'].str.lower().str.contains('media omitted'))
        ]
    def remove_stopwords(message):
        y=[]
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return ' '.join(y)


    temp['message'] = temp['message'].apply(remove_stopwords)
    wc=WordCloud(width=500, height=500,min_font_size=10, background_color='white',)
    df_wc=wc.generate(temp['message'].str.cat(sep=' '))
    return df_wc

def most_common_words(df, selected_user, n):
    import re

    with open('stop_hinglish.txt', 'r') as f:
        stop_words = set(f.read().split())

    # filter user
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[
        (df['user'] != 'group_notification') &
        (~df['message'].str.lower().str.contains('media omitted'))
        ]

    words = []

    for message in temp['message']:
        message = re.sub(r'[^\w\s]', '', message)

        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    return Counter(words).most_common(n)

def monthly_timeline(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + " " + timeline['year'].astype(str)

    return timeline

def monthly_timeline(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month']).count()['message'].reset_index()

    # sort properly
    timeline['month_num'] = pd.to_datetime(timeline['month'], format='%B').dt.month
    timeline = timeline.sort_values(['year', 'month_num'])

    # clean label
    timeline['time'] = pd.to_datetime(
        timeline['month'] + " " + timeline['year'].astype(str)
    ).dt.strftime('%b %Y')

    return timeline

def week_activity(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def hour_activity(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['hour'].value_counts().sort_index()

def activity_heatmap(df, selected_user):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df.pivot_table(index='day_name', columns='hour', values='message', aggfunc='count').fillna(0)