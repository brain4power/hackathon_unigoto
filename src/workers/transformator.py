import logging
from datetime import datetime
from itertools import islice
from typing import Iterable

import faust
from sqlalchemy import update, select, and_, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine

# Project
from config import settings, log_config
from models import *
from sentence_transformers import SentenceTransformer

# init logging
logger = logging.getLogger(__name__)


# models
class MessageKey(faust.Record, serializer="json"):
    message_id: str


class MessageValue(faust.Record, serializer="json"):
    from_page: int


# faust application initialization
app = faust.App(
    settings.TF_APP_NAME,
    broker=f"kafka://{settings.KAFKA_HOST}:{settings.KAFKA_PORT}",
    value_serializer="raw",
    logging_config=log_config,
)

# kafka topic declaration
transformator_task_topic = app.topic(
    settings.TF_TOPIC_NAME,
    key_type=MessageKey,
    value_type=MessageValue,
    partitions=settings.TF_PARTITIONS,
)


def batched(iterable: Iterable, n: int):
    """
    batched('ABCDEFG', 3) --> ABC DEF G
    (from itertools.batched of python 3.12)
    """
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


@app.agent(transformator_task_topic, concurrency=settings.TF_CONCURRENCY)
async def transformator(stream) -> None:
    async for msg_key, msg_value in stream.items():  # type: MessageKey, MessageValue
        logger.info(f"transformator received message with key: {msg_key} and value: {msg_value}")
        db_engine = create_async_engine(
            settings.DATABASE_URI,
            echo=True,
        )
        try:
            async with db_engine.connect() as connection:
                await connection.execute(
                    update(ServiceTask)
                    .where(ServiceTask.record_id == msg_key.message_id)
                    .values(time_task_start=datetime.now())
                )
                await connection.commit()
            logger.info(f"Get model")
            embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            logger.info(f"Model is ready")
            batch_size = settings.TF_PAGE_BATCH_SIZE

            async with db_engine.connect() as connection:
                # update EducationDirection table
                # get values from PG DB
                min_page_query = await connection.execute(
                    select(func.coalesce(func.min(RawData.page_number), 700000))
                )
                to_page = min_page_query.scalar()
                logger.info(f"got to_page: {to_page}")
                logger.info(f"type from_page: {type(msg_value.from_page)}")
                working_from_page = int(msg_value.from_page) - 1
                working_to_page = max(working_from_page - batch_size, to_page)
                while working_from_page >= to_page:
                    # main cycle
                    query = (
                        select(RawData.university_id, RawData.university_name, RawData.faculty_id, RawData.faculty_name)
                        .where(
                            and_(
                                RawData.page_number <= working_from_page,
                                RawData.page_number >= working_to_page,
                                RawData.g_merged_data != "",
                                RawData.university_id != 0,
                                RawData.university_name != "",
                                RawData.faculty_id != 0,
                                RawData.faculty_name != "",
                            ))
                    )
                    logger.info(f"direction query: {query}")
                    query = await connection.execute(query)
                    new_faculty_records = query.fetchall()
                    logger.info(f"Got {len(new_faculty_records)} records")
                    if new_faculty_records:
                        insert_faculty_records_data = [
                            {
                                "university_id": record.university_id,
                                "university_name": record.university_name,
                                "faculty_id": record.faculty_id,
                                "faculty_name": record.faculty_name,
                            }
                            for record in new_faculty_records
                        ]
                        for data_chunk in batched(insert_faculty_records_data, 1000):
                            await connection.execute(
                                insert(EducationDirection)
                                .values(
                                    data_chunk
                                ).on_conflict_do_nothing(index_elements=["faculty_id"])
                            )
                        await connection.commit()
                        logger.info(f"Done insert new EducationDirection")
                    # get new texts
                    query = (
                        select(RawData.record_id, RawData.g_merged_data, EducationDirection.direction_id)
                        .join(EducationDirection, RawData.faculty_id == EducationDirection.faculty_id)
                        .where(
                            and_(
                                RawData.page_number <= working_from_page,
                                RawData.page_number >= working_to_page,
                                RawData.g_merged_data != "",
                            ))
                    )
                    new_records_data = await connection.execute(query)
                    new_records_data = new_records_data.fetchall()
                    if not new_records_data:
                        logger.info(f"len new_records_data: {len(new_records_data)}")
                        task_update_values = {"state": "DONE", "to_page": working_to_page,
                                              "time_task_end": datetime.now()}
                        await connection.execute(
                            update(ServiceTask)
                            .where(ServiceTask.record_id == msg_key.message_id)
                            .values(**task_update_values)
                        )
                        await connection.commit()
                        logging.info(f"Task record with record_id: {msg_key.message_id} was updated as DONE.")
                        return
                    texts = [r.g_merged_data for r in new_records_data]
                    # transform texts to embeddings
                    embeddings = embedding_model.encode(texts)
                    insert_records_data = [
                        {
                            "raw_record_id": record.record_id,
                            "direction_id": record.direction_id,
                            "embedding": embeddings[idx],
                        }
                        for idx, record in enumerate(new_records_data)
                    ]
                    for data_chunk in insert_records_data:
                        await connection.execute(
                            insert(AdditionalData).values(
                                data_chunk
                            ).on_conflict_do_nothing(index_elements=["raw_record_id"])
                        )                    
                    logger.info(f"Done cycle with working_from_page: {working_from_page}, "
                                f"working_to_page: {working_to_page}")
                    # redeclare working pages
                    working_from_page = working_to_page - 1
                    working_to_page = max(working_from_page - batch_size, to_page)

                # filling out the table embeddings
                # select name of programm
                query = (
                        select(ProgrammVector.value, ProgrammVector.direction_id)
                    )
                programm_name_data = await connection.execute(query)
                programm_name_data = programm_name_data.fetchall()
                programm_name_list = [r.value for r in programm_name_data]
                # make embedding for programm name
                programm_embeddings = embedding_model.encode(programm_name_list)
                insert_programm_vec = [
                        {
                            "direction_id": record.direction_id,
                            "embedding": programm_embeddings[idx],
                        }
                        for idx, record in enumerate(programm_name_data)
                    ]
                for data_chunk in insert_programm_vec:
                        await connection.execute(
                            insert(ProgrammVector).values(
                                data_chunk
                            ).on_conflict_do_nothing(index_elements=["direction_id"])

                task_update_values = {"state": "DONE", "to_page": working_from_page + 1,
                                      "time_task_end": datetime.now()}
                await connection.execute(
                    update(ServiceTask)
                    .where(ServiceTask.record_id == msg_key.message_id)
                    .values(**task_update_values)
                )
                await connection.commit()
                logging.info(f"Task record with record_id: {msg_key.message_id} was succeed and updated as DONE.")
        finally:
            await db_engine.dispose()
