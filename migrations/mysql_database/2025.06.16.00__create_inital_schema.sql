start transaction;

create table `user` (
	`id` integer not null auto_increment primary key,
	`document` integer not null,
	`email` varchar(100) not null unique,
	`name` varchar(100) not null,
	`last_name` varchar(100) not null,
	`is_validated` boolean,
	`created_at` datetime not null default current_timestamp,
	`updated_at` datetime not null default current_timestamp on update current_timestamp
);

create table `account` (
	`id` integer not null auto_increment primary key,
	`user_id` integer not null,
	`amount` decimal(20, 4) not null,
	`created_at` datetime not null default current_timestamp,
	`updated_at` datetime not null default current_timestamp on update current_timestamp
);

create table `credit_request` (
	`id` integer not null auto_increment primary key,
	`account_id` integer not null,
	`user_id` integer not null,
	`score` integer,
	`status` integer not null,
	`amount` decimal(20, 4) not null,
	`created_at` datetime not null default current_timestamp,
	`updated_at` datetime not null default current_timestamp on update current_timestamp
);

commit;
