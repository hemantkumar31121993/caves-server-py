drop database if exists caves;
create database caves;
use caves;

-- All the passwords are assumed to be MD5 hashes

create table cred (Team varchar(20) not null, Password char(32) not null, currentlevel Integer not null default 0, WandFound Integer not null, SpiritFreed Integer not null,  primary key(Team));

create table level1 (Team varchar(20) not null, Challenge varchar(512) not null, Password varchar(50) not null, CompletedAt Datetime default null, primary key(Team));

create table level2 (Team varchar(20) not null, Challenge varchar(512) not null, Password varchar(50) not null, CompletedAt Datetime default null, primary key(Team));

create table level3 (Team varchar(20) not null, Challenge varchar(512) not null, Password varchar(50) not null, CompletedAt Datetime default null, primary key(Team));

create table level4 (Team varchar(20) not null, Challenge varchar(50) not null, Password varchar(50) not null, DESKey char(16) not null, CompletedAt Datetime default null, primary key(Team));

create table level5 (Team varchar(20) not null, Challenge varchar(50) not null, Password varchar(50) not null, AMat varchar(300) not null, EVec varchar(60) not null, CompletedAt Datetime default null,  primary key(Team));

create table level6 (Team varchar(20) not null, Challenge varchar(350) not null, Password varchar(50) not null, n varchar(350), p varchar(350), q varchar(350), d varchar(350), e varchar(350), CompletedAt Datetime default null, primary key(Team));

create table level7 (Team varchar(20) not null, Challenge varchar(250) not null, Password varchar(50) not null, CompletedAt Datetime default null, primary key(Team));

