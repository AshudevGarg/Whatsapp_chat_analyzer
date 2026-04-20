import streamlit as st
from matplotlib import pyplot as plt

import preprocessor
import helper
import pandas as pd
st.sidebar.title('Whatsapp Chat Analyzer')


uploaded_file = st.sidebar.file_uploader(
    "Choose a file",
    type=["txt"]
)

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')
    df=preprocessor.preprocess(data)
    # st.dataframe(df)

    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,'Overall')
    selected_user = st.sidebar.selectbox('Whatsapp Chat Analyzer',user_list)

    if st.sidebar.button('Show Analysis'):

        num_messages,words,num_media_messages,num_links = helper.fetch_stats(selected_user,df)
        col1,col2,col3,col4=st.columns(4)
        with col1:
            st.header('Total Messages')
            st.title(num_messages)
        with col2:
            st.header('Total words')
            st.title(words)
        with col3:
            st.header('Media Messages')
            st.title(num_media_messages)
        with col4:
            st.header('Total Links')
            st.title(num_links)

    # Most Busy Users
    if selected_user == 'Overall':
        st.title('Most Busy Users')
        n = st.slider("Select number of top users", 1, 50, 5)
        df = df[df['user'] != 'group_notification']
        x, new_df = helper.most_busy_users(df, n)
        new_df = new_df.head(n)
        col1, col2 = st.columns([2, 1])

        with col1:
            fig, ax = plt.subplots(figsize=(8, 5))
            bars = ax.bar(x.index, x.values, color='skyblue')
            bars[0].set_color('orange')
            for i, v in enumerate(x.values):
                ax.text(i, v + 5, str(v), ha='center')
            ax.set_ylabel("Messages")
            ax.set_title("Top Active Users")
            ax.grid(axis='y', linestyle='--', alpha=0.6)
            plt.xticks(rotation=90)
            st.pyplot(fig)

        with col2:
            st.subheader("User Contribution (%)")
            st.dataframe(
                new_df,
                use_container_width=True,
                height=400
            )

    #word Cloud
    st.title('Word Cloud')
    df_wc=helper.create_word_cloud(selected_user,df)
    fig,ax = plt.subplots()
    ax.imshow(df_wc,cmap='gray')
    st.pyplot(fig)

    n_words = st.slider("Select number of top words", 1, 30, 10)
    st.title(f" Most Common Words ({selected_user})")

    common_words = helper.most_common_words(df, selected_user, n_words)
    df_words = pd.DataFrame(common_words, columns=['Word', 'Frequency'])

    total = df_words['Frequency'].sum()
    df_words['Percent (%)'] = (df_words['Frequency'] / total * 100).round(2)
    top_row = df_words.loc[df_words['Frequency'].idxmax()]

    top_word = top_row['Word']
    top_count = top_row['Frequency']

    st.metric(label="Most Used Word", value=top_word, delta=f"{top_count} times")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Top Words")
        st.dataframe(
            df_words,
            use_container_width=True,
            height=400
        )

    with col2:
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.barh(df_words['Word'], df_words['Frequency'], color='skyblue')
        bars[-1].set_color('orange')
        for i, v in enumerate(df_words['Frequency']):
            ax.text(v + 1, i, str(v), va='center')

        ax.set_xlabel("Frequency")
        ax.set_title("Most Used Words")
        ax.grid(axis='x', linestyle='--', alpha=0.6)
        st.pyplot(fig)

    # Monthly Activity
    st.title("Monthly Activity")
    timeline = helper.monthly_timeline(df, selected_user)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(timeline['time'], timeline['message'], color='blue', marker='o')
    ax.fill_between(timeline['time'], timeline['message'], alpha=0.2)
    max_idx = timeline['message'].idxmax()
    ax.scatter(timeline['time'][max_idx], timeline['message'][max_idx], color='red', s=100, label='Peak')
    ax.legend()
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Messages")
    ax.set_title("Monthly Message Activity")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    for i in range(len(timeline)):
        ax.text(timeline['time'][i], timeline['message'][i], str(timeline['message'][i]), fontsize=8)

    plt.xticks(rotation=90, fontsize=8)
    st.pyplot(fig)

    # Weekly Activity
    st.title("Weekly Activity")
    week = helper.week_activity(df, selected_user)
    order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    week = week.reindex(order)
    week.index = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    fig, ax = plt.subplots()
    ax.bar(week.index, week.values, color='skyblue')
    ax.plot(week.index, week.values, color='red', marker='o')
    ax.set_xlabel("Day")
    ax.set_ylabel("Number of Messages")
    ax.set_title("Weekly Message Activity")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    # Hourly Activity
    st.title("Hourly Activity")
    hour = helper.hour_activity(df, selected_user)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(hour.index, hour.values, color='skyblue')

    ax.plot(hour.index, hour.values, color='red', marker='o')
    max_idx = hour.idxmax()
    ax.scatter(max_idx, hour[max_idx], color='green', s=100, label='Peak Hour')
    ax.legend()
    labels = []
    for i in hour.index:
        if i == 0:
            labels.append("12 AM")
        elif i < 12:
            labels.append(f"{i} AM")
        elif i == 12:
            labels.append("12 PM")
        else:
            labels.append(f"{i - 12} PM")

    ax.set_xticks(hour.index)
    ax.set_xticklabels(labels, rotation=90)
    ax.fill_between(hour.index, hour.values, alpha=0.2)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Number of Messages")
    ax.set_title("Hourly Message Activity")
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig)

    # Heatmap
    import seaborn as sns
    st.title("Activity Heatmap")
    heatmap = helper.activity_heatmap(df, selected_user)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap = heatmap.reindex(day_order)

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(
        heatmap,
        cmap="YlGnBu",
        linewidths=0.5,
        linecolor='white',
        cbar_kws={'label': 'Message Count'},
        ax=ax
    )
    labels = []
    for i in heatmap.columns:
        if i == 0:
            labels.append("12 AM")
        elif i < 12:
            labels.append(f"{i} AM")
        elif i == 12:
            labels.append("12 PM")
        else:
            labels.append(f"{i - 12} PM")

    ax.set_xticklabels(labels, rotation=90)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Day of Week")
    ax.set_title("Weekly Activity Heatmap")

    st.pyplot(fig)