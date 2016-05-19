drop database if exists caves;
create database caves;
use caves;

-- All the passwords are assumed to be MD5 hashes

create table cred (Team varchar(20) not null, Password char(32) not null, currentlevel Integer not null default 0, primary key(Team));

create table level1ques (Team varchar(20) not null, Challenge varchar(50) not null, primary key(Team));
create table level1sol (Team varchar(20) not null, Password varchar(50) not null, primary key(Team));

create table level2ques (Team varchar(20) not null, Challenge varchar(256) not null, primary key(Team));
create table level2sol (Team varchar(20) not null, Password varchar(50) not null, primary key(Team));

create table level3ques (Team varchar(20) not null, Challenge varchar(50) not null, primary key(Team));
create table level3sol (Team varchar(20) not null, Password varchar(50) not null, primary key(Team));

create table level4ques (Team varchar(20) not null, Challenge varchar(50) not null, primary key(Team));
create table level4sol (Team varchar(20) not null, Password varchar(50) not null, primary key(Team));
create table level4keys (Team varchar(20) not null, DESKey char(16) not null, primary key(Team));

create table level5ques (Team varchar(20) not null, Challenge varchar(50) not null, primary key(Team));
create table level5sol (Team varchar(20) not null, Password varchar(50) not null, primary key(Team));
create table level5keys (Team varchar(20) not null, AMat char(112) not null, EVec char(14), primary key(Team));

create table level6ques (Team varchar(20) not null, Challenge varchar(350) not null, n varchar(350), e varchar(350), primary key(Team));
create table level6sol (Team varchar(20) not null, Password varchar(50) not null, primary key(Team));
--create table level6keys (Team varchar(20) not null, p varchar(350), q varchar(350), d varchar(350),  primary key(Team));

create table level7ques (Team varchar(20) not null, Challenge varchar(250) not null, primary key(Team));
create table level7sol (Team varchar(20) not null, Password varchar(50) not null, primary key(Team));

insert into cred values ("a", MD5("a"), 0);

insert into level1ques values ("a", "uhXhQ03nfrv");
insert into level1sol values ("a", MD5("level1"));

insert into level2ques values ("a", "Lg ccud qh urg tgay ejbwdkt, wmgtf su bgud nkudnk lrd vjfbg. Yrhfm qvd vng sfuuxytj \"vkj_ecwo_ogp_ej_rnfkukf\" wt iq urtuwjm. Ocz iqa jdag vio uzthsivi pqx vkj pgyd encpggt. Uy hopg yjg fhkz arz hkscv ckoq pgfn vu wwygt nkioe zttft djkth.");
insert into level2sol values ("a", MD5("the_cave_man_may_be_pleased"));
