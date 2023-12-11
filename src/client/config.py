import os

__all__ = [
    "endpoint_ping",
    "endpoint_search",
    "CONTRIBUTORS_MD",
    "LINKS_MD",
    "REQUEST_BODY",
    "USER_INPUT",
    "METRICS",
]

# api endpoints
endpoint_ping = os.getenv("API_PING_URI")
endpoint_search = os.getenv("API_SEARCH_URI")

# used in st.markdown()
CONTRIBUTORS = [
    {
        "name": "Туомас Эдвард",
        "github": "https://github.com/ToyOwl",
        "role": "Software Developer",
    },
    {
        "name": "Анисимова Татьяна",
        "github": "https://github.com/t-linguist",
        "role": " ML Engineer",
    },
    {
        "name": "Голубев Артём",
        "github": "https://github.com/arqoofficial",
        "role": "Business Analyst",
    },
    {
        "name": "Гуков Алексей",
        "github": "https://github.com/brain4power",
        "role": "MLOps Engineer",
    },
    {
        "name": "Колотий Вячеслав",
        "github": "https://github.com/kv49",
        "role": "PM",
    },
    {
        "name": "Ротерман Виктор",
        "github": "https://github.com/ViktorRtm",
        "role": "Test Automation Engineer",
    },
]
CONTRIBUTORS_MD = [f"[{item['name']}]({item['github']}) – {item['role']}" for item in CONTRIBUTORS]

LINKS = [
    {
        "name": "GitHub",
        "link": "https://github.com/brain4power/hackathon_unigoto",
    },
]
LINKS_MD = [f"[{item['name']}]({item['link']})" for item in LINKS]

# input
REQUEST_BODY = {
    "city_title": "",
    "about": "",
    "activities": "",
    "books": "",
    "games": "",
    "interests": "",
    "threshold": 0,
    "limit": 15,
}

USER_INPUT = [
    {
        "option": "city_title",
        "markdown": "Название города",
        "example": "Москва",
    },
    {
        "option": "about",
        "markdown": "О себе",
        "example": "Студент",
    },
    {
        "option": "activities",
        "markdown": "Вид деятельности",
        "example": "Программирование, математика",
    },
    {
        "option": "books",
        "markdown": "Любимые книги",
        "example": "Задачи по математике",
    },
    {
        "option": "games",
        "markdown": "Любимые игры",
        "example": "Стратегии",
    },
    {
        "option": "interests",
        "markdown": "Интересы",
        "example": "Музыка, велосипед",
    },
]

# table
METRICS = [
    "cosine_distance",
]
