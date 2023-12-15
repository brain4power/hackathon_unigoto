
--truncate table h_edu_direction;
create table h_edu_direction
(
	direction_id uuid NOT NULL DEFAULT gen_random_uuid(),
	value VARCHAR,
	embedding public.vector,
	CONSTRAINT h_edu_direction_pkey PRIMARY KEY (direction_id)
);

--drop table h_edu_universities;
--truncate h_edu_universities;
create table h_edu_universities
(
	university_id uuid NOT NULL DEFAULT gen_random_uuid(),
	full_name varchar NOT NULL,
	postcode varchar,
	city varchar,
	longitude float,
	latitude float,
	CONSTRAINT h_edu_universities_pkey PRIMARY KEY (university_id)
);

--truncate h_edu_direct2univ;
create table h_edu_direct2univ
(
    direction_id uuid NOT null,
    university_id uuid NOT NULL,
   	CONSTRAINT h_edu_direct2univ_pkey PRIMARY KEY (direction_id, university_id)
);

create table h_faculty_2_ru
(
    faculty_name varchar,
    faculty_name_fixed_ru varchar,
   	CONSTRAINT h_faculty_2_ru_pkey PRIMARY KEY (faculty_name)
);

--drop table h_faculties_ru;
create table h_faculties_ru
(
    faculty_name_fixed_ru varchar,
    popularity int,
	embedding public.vector,
   	CONSTRAINT h_faculties_ru_pkey PRIMARY KEY (faculty_name_fixed_ru)
);


--drop function get_haversine_distance(lat1 float, lng1 float, lat2 float, lng2 float);
create or replace function get_haversine_distance(lat1 float, lng1 float, lat2 float, lng2 float)
returns float
language plpgsql
as
$$
declare
  lat1r float;
  lng1r float;
  lat2r float;
  lng2r float;
  lat_delta float;
  lng_delta float;
  d float;
  h float;
  tmp float;
  EARTH_RADIUS float;
begin
	EARTH_RADIUS  := 6371;
    lat1r := radians(lat1);
    lng1r := radians(lng1);
    lat2r := radians(lat2);
    lng2r := radians(lng2);

   if lat1r < lat2r then
       tmp := lat1r;
       lat1r := lat2r;
       lat2r := tmp;
   end if;

   if lng1r < lng2r then
       tmp := lng1r;
       lng1r := lng2r;
       lng2r := tmp;
   end if;

    lat_delta := lat2r - lat1r;
    lng_delta := lng2r - lng1r;

    d = power(sin(lat_delta * 0.5),2) + cos(lat1r) * cos(lat2r) * power(sin(lng_delta * 0.5), 2);
    h = 2 * EARTH_RADIUS * asin(sqrt(d));
   return h;
end;
$$;
