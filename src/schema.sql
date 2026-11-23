-- Nexus database schema (SQLite)
-- Generated from the SQLAlchemy models in app/models/.
-- The application creates these tables automatically; this file documents
-- the schema for the Phase 4 deliverable package.

CREATE TABLE body_measurements (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	measured_on DATE NOT NULL, 
	kind VARCHAR(40) NOT NULL, 
	value NUMERIC(10, 2) NOT NULL, 
	unit VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE fitness_goals (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	goal_type VARCHAR(50) NOT NULL, 
	description TEXT NOT NULL, 
	target_value NUMERIC(10, 2), 
	target_date DATE, 
	status VARCHAR(20) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE food_items (
	id INTEGER NOT NULL, 
	name VARCHAR(160) NOT NULL, 
	serving_unit VARCHAR(40) NOT NULL, 
	calories_per_unit NUMERIC(10, 2) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_body_measurements_user_id ON body_measurements (user_id);

CREATE INDEX ix_fitness_goals_user_id ON fitness_goals (user_id);

CREATE INDEX ix_meal_entries_user_id ON meal_entries (user_id);

CREATE INDEX ix_workout_entries_user_id ON workout_entries (user_id);

CREATE TABLE meal_entries (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	food_id INTEGER NOT NULL, 
	eaten_on DATE NOT NULL, 
	meal_label VARCHAR(32) NOT NULL, 
	quantity NUMERIC(10, 2) NOT NULL, 
	calorie_snapshot NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(food_id) REFERENCES food_items (id)
);

CREATE TABLE profiles (
	user_id INTEGER NOT NULL, 
	display_name VARCHAR(100) NOT NULL, 
	preferences TEXT, 
	daily_calorie_target NUMERIC(8, 2), 
	PRIMARY KEY (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE reset_tokens (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	token_hash TEXT NOT NULL, 
	expires_at DATETIME NOT NULL, 
	used_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE users (
	id INTEGER NOT NULL, 
	email VARCHAR(254) NOT NULL, 
	password_hash TEXT NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (email)
);

CREATE TABLE workout_entries (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	activity_type VARCHAR(80) NOT NULL, 
	started_at DATETIME NOT NULL, 
	duration_minutes INTEGER NOT NULL, 
	estimated_kcal NUMERIC(8, 2), 
	notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

