drop database if exists caves;
create database caves;
use caves;

-- All the passwords are assumed to be MD5 hashes

create table cred (Team varchar(20) not null, Password char(32) not null, currentlevel Integer not null default 0, WandFound Integer not null, SpiritFreed Integer not null,  primary key(Team));

create table level1 (Team varchar(20) not null, Challenge varchar(50) not null, Password varchar(50) not null, primary key(Team));

create table level2 (Team varchar(20) not null, Challenge varchar(256) not null, Password varchar(50) not null, primary key(Team));

create table level3 (Team varchar(20) not null, Challenge varchar(350) not null, Password varchar(50) not null, primary key(Team));

create table level4 (Team varchar(20) not null, Challenge varchar(50) not null, Password varchar(50) not null, DESKey char(16) not null, primary key(Team));

create table level5 (Team varchar(20) not null, Challenge varchar(50) not null, Password varchar(50) not null, AMat varchar(300) not null, EVec varchar(60) not null,  primary key(Team));

create table level6 (Team varchar(20) not null, Challenge varchar(350) not null, Password varchar(50) not null, n varchar(350), p varchar(350), q varchar(350), d varchar(350), e varchar(350), primary key(Team));

create table level7 (Team varchar(20) not null, Challenge varchar(250) not null, Password varchar(50) not null, primary key(Team));

insert into cred values ("a", MD5("a"), 0, 0, 0);

insert into level1 values ("a", "uhXhQ03nfrv", MD5("level1"));

insert into level2 values ("a", "Lg ccud qh urg tgay ejbwdkt, wmgtf su bgud nkudnk lrd vjfbg. Yrhfm qvd vng sfuuxytj \"vkj_ecwo_ogp_ej_rnfkukf\" wt iq urtuwjm. Ocz iqa jdag vio uzthsivi pqx vkj pgyd encpggt. Uy hopg yjg fhkz arz hkscv ckoq pgfn vu wwygt nkioe zttft djkth.", MD5("level2"));

insert into level3 values ("a", "Lg ccud qh urg tgay ejbwdkt, wmgtf su bgud nkudnk lrd vjfbg. Yrhfm qvd vng sfuuxytj \"vkj_ecwo_ogp_ej_rnfkukf\" wt iq urtuwjm. Ocz iqa jdag vio uzthsivi pqx vkj pgyd encpggt. Uy hopg yjg fhkz arz hkscv ckoq pgfn vu wwygt nkioe zttft djkth.", MD5("level3"));

insert into level4 values("a", "1234567890abcdef1234567890abcdef", MD5("level4"), "ab12acf45c8f6acc");

insert into level5 values("a", "1234567890abcdef1234567890abcdef", MD5("level5"), "12 65 89 78 45 12 65 89;12 45 69 87 120 25 78 45;12 65 98 74 56 23 58 78;45 98 56 32 56 78 78 78;12 45 98 56 32 55 46 92;12 56 98 73 19 65 74 32;14 69 81 37 12 97 12 36;12 65 89 78 41 39 87 12", "1 5 98 45 125 12 49 37");

insert into level6 values("a", "456958", MD5("level6"), "4456", "165", "541", "45", "45");

insert into level7 values("a", "12 25 45 68 98 56 25 69 85 41 25 63 25 65 89 54 12 56 58 45 12 55 33 22 45 65 89 45 12 55 66 55 45", MD5("level7"));
