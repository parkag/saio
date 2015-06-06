DROP SCHEMA IF EXISTS test_view CASCADE;
CREATE SCHEMA test_view;
SET SEARCH_PATH = test_view, test_data;


CREATE TABLE friend_relation (
	are_friends BOOLEAN NOT NULL, 
	user_id_1 INTEGER NOT NULL, 
	user_id_2 INTEGER NOT NULL
);



CREATE TABLE facebook_group (
	creator INTEGER NOT NULL, 
	description VARCHAR(1000), 
	group_id INTEGER NOT NULL, 
	group_sub_type INTEGER, 
	group_type INTEGER, 
	large_picture VARCHAR(1000), 
	medium_picture VARCHAR(1000), 
	name VARCHAR(1000), 
	network_id INTEGER, 
	recent_news VARCHAR(1000), 
	small_picture VARCHAR(1000), 
	updated_time TIMESTAMP WITHOUT TIME ZONE, 
	website VARCHAR(1000)
);



CREATE TABLE event_membership (
	user_id INTEGER NOT NULL, 
	status VARCHAR(1000)
);



CREATE TABLE facebook_event (
	creator INTEGER NOT NULL, 
	description VARCHAR(1000), 
	end_time TIMESTAMP WITHOUT TIME ZONE, 
	event_id INTEGER NOT NULL, 
	event_sub_type INTEGER, 
	event_type INTEGER, 
	host INTEGER, 
	large_picture VARCHAR(1000), 
	location VARCHAR(1000), 
	medium_picture VARCHAR(1000), 
	name VARCHAR(1000), 
	network_id INTEGER, 
	small_picture VARCHAR(1000), 
	start_time TIMESTAMP WITHOUT TIME ZONE, 
	tag_line INTEGER, 
	updated_time TIMESTAMP WITHOUT TIME ZONE
);



CREATE TABLE location (
	city VARCHAR(200), 
	country VARCHAR(200), 
	state VARCHAR(200), 
	street VARCHAR(200), 
	zip_code VARCHAR(100)
);



CREATE TABLE user_status (
	status VARCHAR(200), 
	update_time TIMESTAMP WITHOUT TIME ZONE
);



CREATE TABLE affiliation (
	name VARCHAR(200), 
	nid INTEGER, 
	status VARCHAR(200), 
	year INTEGER
);



CREATE TABLE photo_album (
	album_id INTEGER, 
	cover_photo_id INTEGER, 
	created TIMESTAMP WITHOUT TIME ZONE, 
	description VARCHAR(200), 
	location VARCHAR(1000), 
	modified TIMESTAMP WITHOUT TIME ZONE, 
	name VARCHAR(200), 
	size INTEGER,
	user_id INTEGER NOT NULL
);



CREATE TABLE photo (
	album_id INTEGER, 
	cover_photo_id INTEGER, 
	created TIMESTAMP WITHOUT TIME ZONE, 
	large_source VARCHAR, 
	link VARCHAR(1000), 
	medium_source VARCHAR(1000), 
	owner INTEGER, 
	photo_id INTEGER, 
	small_source VARCHAR(200)
);



CREATE TABLE workplace (
	company_name VARCHAR(1000), 
	description VARCHAR, 
	end_date TIMESTAMP WITHOUT TIME ZONE, 
	position VARCHAR(100), 
	start_date TIMESTAMP WITHOUT TIME ZONE
);



CREATE TABLE facebook_profile (
	about_me VARCHAR(1000), 
	activities VARCHAR(1000), 
	affiliation_count INTEGER, 
	birthday TIMESTAMP WITHOUT TIME ZONE, 
	favorite_books VARCHAR, 
	favorite_movies VARCHAR, 
	favorite_music VARCHAR, 
	favorite_quotes VARCHAR, 
	favorite_tv_shows VARCHAR, 
	first_name VARCHAR(200), 
	interests VARCHAR, 
	is_application_user BOOLEAN, 
	last_name VARCHAR(200), 
	notes_count INTEGER, 
	picture_big_url VARCHAR(1000), 
	picture_small_url VARCHAR(1000), 
	political_views VARCHAR(100), 
	religion VARCHAR(100), 
	school_count INTEGER, 
	significant_other_id INTEGER, 
	update_time TIMESTAMP WITHOUT TIME ZONE, 
	user_id INTEGER NOT NULL, 
	wall_count INTEGER, 
	web_add_friend_link VARCHAR, 
	web_notes_by_user_link VARCHAR, 
	web_pictures_of_user_link VARCHAR, 
	web_poke_link VARCHAR, 
	web_post_on_user_wall_link VARCHAR, 
	web_profile_link VARCHAR, 
	web_send_message_link VARCHAR, 
	work_place_count INTEGER
);



CREATE TABLE school (
	concentrations VARCHAR(200), 
	graduation_year INTEGER, 
	name VARCHAR(200), 
	school_id INTEGER NOT NULL
);



CREATE TABLE photo_tag (
	photo_id INTEGER NOT NULL, 
	position VARCHAR, 
	user_id INTEGER NOT NULL
);



CREATE TABLE tracking_data (
	user_id INTEGER NOT NULL, 
	time TIMESTAMP WITHOUT TIME ZONE, 
	location VARCHAR
);



CREATE OR REPLACE VIEW spy_view AS
	SELECT fb1.first_name, fb1.last_name, tracking_data.time, tracking_data.location, COUNT(friend_relation)
	FROM tracking_data
	JOIN facebook_profile fb1 ON (tracking_data.user_id = fb1.user_id)
	LEFT JOIN facebook_profile fb2 ON (fb1.significant_other_id = fb2.user_id)
	JOIN friend_relation ON (friend_relation.user_id = fb1.user_id)
	JOIN photo_album ON (photo_album.user_id = fb1.user_id)
	JOIN photo ON ()

	WHERE COUNT(friend_relation) > 500 AND fb1.birthday > '1969-01-01'
;

EXPLAIN (FORMAT JSON) FROM spy_view;