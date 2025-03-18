import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

st.sidebar.title("📱 WhatsApp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("📂 Upload a chat file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # Fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("👤 Show analysis for", user_list)

    if st.sidebar.button("🔍 Show Analysis"):

        # Top Statistics
        st.title("📊 Top Statistics")
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Messages", num_messages)
        with col2:
            st.metric("Total Words", words)
        with col3:
            st.metric("Media Shared", num_media_messages)
        with col4:
            st.metric("Links Shared", num_links)

        # Monthly & Daily Timeline
        st.title("📅 Message Timeline")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📆 Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(timeline['time'], timeline['message'], color='green', marker='o', linestyle='-')
            plt.xticks(rotation=45, fontsize=8)
            plt.xlabel("Month-Year", fontsize=10)
            plt.ylabel("Messages", fontsize=10)
            plt.grid(True, linestyle="--", alpha=0.5)
            st.pyplot(fig)

        with col2:
            st.subheader("📅 Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black', marker='o', linestyle='-')
            plt.xticks(rotation=45, fontsize=8)
            plt.xlabel("Date", fontsize=10)
            plt.ylabel("Messages", fontsize=10)
            plt.grid(True, linestyle="--", alpha=0.5)
            st.pyplot(fig)

        # Activity Map
        st.title('🗺️ Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📌 Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(busy_day.index, busy_day.values, color='purple', alpha=0.7)
            plt.xticks(rotation=45, fontsize=8)
            plt.xlabel("Day", fontsize=10)
            plt.ylabel("Messages", fontsize=10)
            plt.grid(axis="y", linestyle="--", alpha=0.5)
            st.pyplot(fig)

        with col2:
            st.subheader("📌 Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(busy_month.index, busy_month.values, color='orange', alpha=0.7)
            plt.xticks(rotation=45, fontsize=8)
            plt.xlabel("Month", fontsize=10)
            plt.ylabel("Messages", fontsize=10)
            plt.grid(axis="y", linestyle="--", alpha=0.5)
            st.pyplot(fig)

        # Weekly Heatmap
        st.title("🗓️ Weekly Activity Heatmap")
        with st.container():
            user_heatmap = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots(figsize=(10, 4))
            sns.heatmap(user_heatmap, cmap="coolwarm", annot=True, fmt=".0f", linewidths=0.5, linecolor='gray')
            plt.xlabel("Hour of Day", fontsize=10)
            plt.ylabel("Day of Week", fontsize=10)
            st.pyplot(fig)

        # Most Busy Users
        if selected_user == 'Overall':
            st.title('🔥 Most Active Users')
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📊 Active Users Count")
                x, new_df = helper.most_busy_users(df)
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.bar(x.index, x.values, color='red', alpha=0.7)
                plt.xticks(rotation=45, fontsize=8)
                plt.xlabel("Users", fontsize=10)
                plt.ylabel("Messages", fontsize=10)
                st.pyplot(fig)

            with col2:
                st.subheader("📊 User Activity (%)")
                st.dataframe(new_df)

        # WordCloud
        st.title("☁️ WordCloud")
        with st.container():
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.imshow(df_wc)
            ax.axis("off")  # Hide axis labels
            st.pyplot(fig)

        # Most Common Words
        st.title("📌 Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        with st.container():
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.barh(most_common_df[0], most_common_df[1], color="blue", alpha=0.7)
            plt.xlabel("Frequency", fontsize=10)
            plt.ylabel("Words", fontsize=10)
            plt.xticks(fontsize=8)
            st.pyplot(fig)

        # Emoji Analysis
        st.title("😃 Emoji Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🔢 Emoji Data")
            emoji_df = helper.emoji_helper(selected_user, df)
            st.dataframe(emoji_df)

        with col2:
            if not emoji_df.empty:  # ✅ Prevents error if no emojis are found
                st.subheader("📊 Emoji Distribution")
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.pie(emoji_df["Count"].head(), labels=emoji_df["Emoji"].head(), autopct="%0.2f")
                st.pyplot(fig)
            else:
                st.write("No emojis found in the selected data.")
