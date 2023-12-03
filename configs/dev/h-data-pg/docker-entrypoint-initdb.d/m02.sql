create table h_raw_data
(
    record_id        uuid      default gen_random_uuid()                                                            not null
        primary key,
    time_created     timestamp default now()                                                                        not null,
    time_updated     timestamp default now()                                                                        not null,
    meta_data        jsonb,
    page_number      integer                                                                                        not null,
    deactivated      varchar                                                                                        not null,
    country_id       integer                                                                                        not null,
    country_title    varchar                                                                                        not null,
    city_id          integer                                                                                        not null,
    city_title       varchar                                                                                        not null,
    about            varchar                                                                                        not null,
    activities       varchar                                                                                        not null,
    books            varchar                                                                                        not null,
    games            varchar                                                                                        not null,
    interests        varchar                                                                                        not null,
    education_form   varchar                                                                                        not null,
    education_status varchar                                                                                        not null,
    university_id    integer                                                                                        not null,
    university_name  varchar                                                                                        not null,
    faculty_id       integer                                                                                        not null,
    faculty_name     varchar                                                                                        not null,
    graduation_year  integer                                                                                        not null,
    g_merged_data    varchar generated always as ((h_concat_string_normalize(country_title, city_title, about,
                                                                             activities, books, games,
                                                                             interests))::character varying) stored not null
);

alter table h_raw_data
    owner to h_user;