import streamlit as st
from matplotlib import pyplot as plt
import preprocessor
import helper
import pandas as pd
import seaborn as sns

st.set_page_config(page_title="WhatsApp Analyzer", layout="wide")

st.sidebar.title('📊 Whatsapp Chat Analyzer')

uploaded_file = st.sidebar.file_uploader("Choose a file", type=["txt"])

if uploaded_file is not None:
    try:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode('utf-8')

        df = preprocessor.preprocess(data)

        if df.empty:
            st.error("No data found in file!")
            st.stop()

        user_list = df['user'].dropna().unique().tolist()
        user_list = [user for user in user_list if user != 'group_notification']

        if not user_list:
            st.error("No valid users found!")
            st.stop()

        user_list.sort()
        user_list.insert(0, 'Overall')

        selected_user = st.sidebar.selectbox('Select User', user_list)

        # STATS
        if st.sidebar.button('Show Analysis'):

            num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

            col1, col2, col3, col4 = st.columns(4)

            col1.metric('Total Messages', num_messages)
            col2.metric('Total Words', words)
            col3.metric('Media Messages', num_media_messages)
            col4.metric('Links', num_links)

        st.markdown("---")

        # MOST BUSY USERS
        if selected_user == 'Overall':
            st.title('👥 Most Busy Users')

            n = st.slider("Select number of top users", 1, 50, 5)

            df_filtered = df[df['user'] != 'group_notification']

            if not df_filtered.empty:
                x, new_df = helper.most_busy_users(df_filtered, n)
                new_df = new_df.head(n)

                col1, col2 = st.columns([2, 1])

                with col1:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    bars = ax.bar(x.index, x.values, color='skyblue')
                    bars[0].set_color('orange')

                    # for i, v in enumerate(x.values):
                    #     ax.text(i, v + 5, str(v), ha='center', fontsize=8)

                    ax.set_ylabel("Messages")
                    ax.set_title("Top Active Users")
                    ax.grid(axis='y', linestyle='--', alpha=0.6)
                    plt.xticks(rotation=90)

                    st.pyplot(fig)

                with col2:
                    st.subheader("📋 Contribution (%)")
                    st.dataframe(new_df, use_container_width=True, height=400)

        st.markdown("---")

        # WORD CLOUD
        st.title('☁️ Word Cloud')

        try:
            df_wc = helper.create_word_cloud(selected_user, df)
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.imshow(df_wc, cmap='viridis')
            ax.axis('off')
            st.pyplot(fig)
        except:
            st.warning("Word cloud not available")

        st.markdown("---")

        # MOST COMMON WORDS
        n_words = st.slider("Top words", 1, 30, 10)

        common_words = helper.most_common_words(df, selected_user, n_words)

        if common_words:
            df_words = pd.DataFrame(common_words, columns=['Word', 'Frequency'])

            if not df_words.empty:
                total = df_words['Frequency'].sum()
                df_words['Percent (%)'] = (df_words['Frequency'] / total * 100).round(2)

                top_row = df_words.loc[df_words['Frequency'].idxmax()]

                st.metric("🔥 Most Used Word", top_row['Word'], f"{top_row['Frequency']} times")

                col1, col2 = st.columns([1, 2])

                with col1:
                    st.dataframe(df_words, use_container_width=True, height=400)

                with col2:
                    fig, ax = plt.subplots(figsize=(8, 5))

                    bars = ax.barh(df_words['Word'], df_words['Frequency'], color='skyblue')
                    bars[-1].set_color('orange')

                    # for i, v in enumerate(df_words['Frequency']):
                    #     ax.text(v + 1, i, str(v), va='center')

                    ax.set_xlabel("Frequency")
                    ax.set_title("Most Used Words")
                    ax.grid(axis='x', linestyle='--', alpha=0.6)

                    st.pyplot(fig)

        st.markdown("---")

        # MONTHLY TIMELINE
        st.title("📅 Monthly Activity")

        timeline = helper.monthly_timeline(df, selected_user)

        if not timeline.empty:
            fig, ax = plt.subplots(figsize=(10, 5))

            ax.plot(timeline['time'], timeline['message'], color='blue', marker='o')
            ax.fill_between(timeline['time'], timeline['message'], alpha=0.2)

            max_idx = timeline['message'].idxmax()
            ax.scatter(timeline['time'][max_idx], timeline['message'][max_idx], color='red', s=100)

            ax.set_xlabel("Month")
            ax.set_ylabel("Messages")
            ax.set_title("Monthly Activity")
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            plt.xticks(rotation=90, fontsize=8)

            st.pyplot(fig)

        st.markdown("---")

        # WEEKLY
        st.title("📆 Weekly Activity")

        week = helper.week_activity(df, selected_user)

        if not week.empty:
            order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            week = week.reindex(order)
            week.index = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

            fig, ax = plt.subplots()

            ax.bar(week.index, week.values, color='skyblue')
            ax.plot(week.index, week.values, color='red', marker='o')

            ax.set_xlabel("Day")
            ax.set_ylabel("Messages")
            ax.set_title("Weekly Activity")
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            st.pyplot(fig)

        st.markdown("---")

        # HOURLY
        st.title("⏰ Hourly Activity")

        hour = helper.hour_activity(df, selected_user)

        if not hour.empty:
            fig, ax = plt.subplots(figsize=(10, 5))

            ax.bar(hour.index, hour.values, color='skyblue')
            ax.plot(hour.index, hour.values, color='red', marker='o')

            labels = []
            for i in hour.index:
                if i == 0:
                    labels.append("12 AM")
                elif i < 12:
                    labels.append(f"{i} AM")
                elif i == 12:
                    labels.append("12 PM")
                else:
                    labels.append(f"{i-12} PM")

            ax.set_xticks(hour.index)
            ax.set_xticklabels(labels, rotation=90)

            ax.fill_between(hour.index, hour.values, alpha=0.2)

            ax.set_xlabel("Hour")
            ax.set_ylabel("Messages")
            ax.set_title("Hourly Activity")

            st.pyplot(fig)

        st.markdown("---")

        # HEATMAP
        st.title("🔥 Activity Heatmap")

        heatmap = helper.activity_heatmap(df, selected_user)

        if not heatmap.empty:
            fig, ax = plt.subplots(figsize=(12, 5))

            sns.heatmap(
                heatmap,
                cmap="YlGnBu",
                linewidths=0.5,
                linecolor='white',
                cbar_kws={'label': 'Messages'},
                ax=ax
            )

            ax.set_title("Weekly Activity Heatmap")

            st.pyplot(fig)

    except Exception as e:
        st.error(f"Something went wrong: {e}")