import os
import time
from collections.abc import Iterable
from datetime import datetime
from functools import partial
from uuid import uuid4

import pandas as pd
import requests
import streamlit as st

from config import CONTRIBUTORS, LINKS

endpoint_ping = os.getenv("API_PING_URI")
endpoint_search = os.getenv("API_SEARCH_URI")
st.text_input = partial(st.text_input, label_visibility="collapsed")


def _run_id() -> str:
    """Generates unique thread-save and multi-machine-resistant folder name for a single run, based on time"""
    return (
        datetime.now().astimezone().strftime("%Y-%m-%d--TZ%z-%H-%M-%S")
        + "--"
        + str(uuid4())
    )


def _write_list(input: Iterable) -> None:
    for item in input:
        st.markdown(f"* {item}")


def call_api_get(url: str) -> dict:
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"error {response.status_code} {response.content}")
    return response.json()


def call_api_post(url: str, request: dict) -> dict:
    response = requests.post(
        url,
        json=request,
        timeout=8000,
    )
    if response.status_code != 200:
        st.error(f"error {response.status_code} {response.content}")
    return response.json()


def parse_response(response: dict, show_id: bool) -> pd.DataFrame:
    df = pd.DataFrame(response["items"])
    df.index = df.index + 1
    if not show_id:
        df.drop(columns=[col for col in df.columns if "_id" in col], inplace=True)
    return df


def main():
    # sidebar
    with st.sidebar:
        st.markdown(
            "# Big Uh + UniToGo 👨‍🎓👩‍🎓\n"
            "С помощью нашего приложения ты сможешь подобрать себе лучший университет!\n"
        )
        with st.expander("Продвинутые настройки"):
            limit = st.slider(
                "Лимит выдачи результатов",
                min_value=1,
                max_value=50,
                value=15,
                step=1,
            )
            show_id = st.checkbox("Показывать id")

        st.markdown("## Информация")
        with st.expander("Участники"):
            _write_list(CONTRIBUTORS)
        with st.expander("Ссылки"):
            _write_list(LINKS)
        with st.expander("Проверить работу API"):
            if st.button("Ping"):
                response = call_api_get(endpoint_ping)
                success = st.success(response["response"])
                time.sleep(1)
                success.empty()

    # Main page
    st.markdown("## Расскажи нам про себя")
    with st.expander("Здесь находятся поля для заполнения", expanded=True):
        # shit happens...
        if st.checkbox("Заполнить автоматически  / очистить поля"):
            st.markdown("##### Название города")
            city_title = st.text_input("1", "Москва")

            st.markdown("##### О себе")
            about = st.text_input("2", "Студент")

            st.markdown("##### Вид деятельности")
            activities = st.text_input("3", "Программирование, математика")

            st.markdown("##### Любимые книги")
            books = st.text_input("4", "Задачи по математике")

            st.markdown("##### Любимые игры")
            games = st.text_input("5", "Стратегии")

            st.markdown("##### Интересы")
            interests = st.text_input("6", "Музыка, велосипед")
        else:
            st.markdown("##### Название города")
            city_title = st.text_input("1")

            st.markdown("##### О себе")
            about = st.text_input("2")

            st.markdown("##### Вид деятельности")
            activities = st.text_input("3")

            st.markdown("##### Любимые книги")
            books = st.text_input("4")

            st.markdown("##### Любимые игры")
            games = st.text_input("5")

            st.markdown("##### Интересы")
            interests = st.text_input("6")

    request = {
        "city_title": city_title,
        "about": about,
        "activities": activities,
        "books": books,
        "games": games,
        "interests": interests,
        "limit": limit,
    }

    if st.button("Отправить на анализ", use_container_width=True):
        with st.spinner("Wait for it..."):
            response = call_api_post(endpoint_search, request)
        st.success("Done!")
        st.markdown("## Результаты анализа")
        result_table = parse_response(response, show_id)
        st.download_button(
            label="Скачать таблицу",
            data=result_table.to_csv().encode("utf-8"),
            file_name=f"{_run_id()}.csv",
            mime="text/csv",
            help="В формате csv",
        )
        st.table(result_table)


if __name__ == "__main__":
    st.set_page_config(page_title="Подбор университета")
    main()
