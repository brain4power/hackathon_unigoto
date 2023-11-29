import asyncio
from copy import deepcopy

import requests
from furl import furl
from sqlalchemy import insert

# Project
from config import Database
from models import RawData


base_api_url = furl("http://45.91.8.110/api/")
access_token = ""
timeout = 11


async def async_main() -> None:
    start_page_number = 698500
    error_count = 10
    db = Database()
    engine = db.engine

    while start_page_number > 0 and error_count > 0:
        api_url = deepcopy(base_api_url)
        api_url.path.add(str(start_page_number))
        print(f"Ready to get request to url: {api_url.url}")
        response = requests.get(api_url.url, params={"token": access_token})
        if response.status_code != 200:
            print(f"Got {response.status_code} status_code. Will take a nap")
            error_count -= 1
            await asyncio.sleep(timeout)
            continue
        data = [
            dict(
                page_number=start_page_number,
                deactivated=el.get("deactivated"),
                country_id=el.get("country").get("id"),
                country_title=el.get("country").get("title"),
                city_id=el.get("city").get("id"),
                city_title=el.get("city").get("title"),
                about=el.get("about"),
                activities=el.get("activities"),
                books=el.get("books"),
                games=el.get("games"),
                interests=el.get("interests"),
                education_form=el.get("education_form"),
                education_status=el.get("education_status"),
                university_id=el.get("university"),
                university_name=el.get("university_name"),
                faculty_id=el.get("faculty"),
                faculty_name=el.get("faculty_name"),
                graduation_year=el.get("graduation"),
            )
            for el in response.json()["response"]
        ]
        async with engine.begin() as conn:
            await conn.execute(insert(RawData), data)
            await conn.commit()
        await engine.dispose()
        print(f"Done save data for page: {start_page_number}")
        start_page_number -= 1
        print("Will take a nap...")
        await asyncio.sleep(timeout)
        print("Continue collect data")
    print(f"Done collect data.")


asyncio.run(async_main())
