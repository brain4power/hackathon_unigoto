import os
import time
from collections.abc import Iterable
from datetime import datetime
from functools import partial
from typing import Literal
from uuid import uuid4

import pandas as pd
import requests
import streamlit as st

from config import CONTRIBUTORS_MD, LINKS_MD, METRICS, REQUEST_BODY, USER_INPUT

endpoint_ping = os.getenv("API_PING_URI")
endpoint_search = os.getenv("API_SEARCH_URI")
st.text_input = partial(st.text_input, label_visibility="collapsed")


def _run_id() -> str:
    return f"{datetime.now().astimezone().strftime('%Y-%m-%d--TZ%z-%H-%M-%S')}--{uuid4()}"


def _write_as_list(input: Iterable) -> None:
    for item in input:
        st.markdown(f"* {item}")


def call_api(
    url: str,
    request: dict = None,
    call_type: Literal["get", "post"] = "get",
) -> dict:
    if call_type == "get":
        response = requests.get(url)
    elif call_type == "post":
        response = requests.post(
            url,
            json=request,
            timeout=180,
        )
    else:
        raise ValueError(f"`call_type` should be 'get' or 'post', not `{call_type}`")
    if response.status_code != 200:
        st.error(f"error {response.status_code} {response.content}")
    return response.json()


def parse_response(
    response: dict,
    show_id: bool = False,
    show_metrics: bool = False,
) -> pd.DataFrame:
    df = pd.DataFrame(response["items"])
    df.index = df.index + 1
    if not show_id:
        df.drop(columns=[col for col in df.columns if "_id" in col], inplace=True)
    if not show_metrics:
        df.drop(columns=METRICS, inplace=True)
    return df


def main():
    # Sidebar
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
            threshold = st.slider(
                "Порог",
                min_value=0.0,
                max_value=1.0,
                value=1.0,
                step=0.05,
            )
            show_id = st.checkbox("Показывать id")
            show_metrics = st.checkbox("Показывать метрики")
        with st.expander("Проверить работу API"):
            if st.button("Ping"):
                response = call_api(endpoint_ping)
                success = st.success(response["response"])
                time.sleep(1)
                success.empty()
        st.markdown("## Информация")
        with st.expander("Участники"):
            _write_as_list(CONTRIBUTORS_MD)
        with st.expander("Ссылки"):
            _write_as_list(LINKS_MD)

    # User input
    st.markdown("## Расскажи нам про себя")
    with st.expander("Здесь находятся поля для заполнения", expanded=True):
        auto_fill = st.checkbox("Заполнить автоматически  / очистить поля")
        request = REQUEST_BODY.copy()
        for index, item in enumerate(USER_INPUT):
            st.markdown(f"##### {item['markdown']}")
            if auto_fill:
                request[item["option"]] = st.text_input(f"{index}", item["example"])
            else:
                request[item["option"]] = st.text_input(f"{index}")
    request["limit"] = limit
    request["threshold"] = threshold

    # Analysis and results
    if st.button("Отправить на анализ", use_container_width=True):
        with st.spinner("Обработка..."):
            response = call_api(endpoint_search, request, "post")
        st.success("Done!")
        st.markdown("## Результаты анализа")
        result_table = parse_response(response, show_id, show_metrics)
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
