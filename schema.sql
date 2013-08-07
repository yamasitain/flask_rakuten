drop table if exists ritem;
create table ritem (
  id integer primary key autoincrement,
  name string not null,
  catch string not null,
  code string not null,
  url string not null,
  imgurl string not null,
  shopcode string not null,
  genreid string not null,
  date integer not null
);

drop table if exists rshop;
create table rshop (
  id integer primary key autoincrement,
  itemcode string not null,
  shopcode string not null,
  shopname string not null,
  shopurl string not null,
  genreid string not null,
  date integer not null
);

drop table if exists rwindow;
create table rwindow (
  id integer primary key autoincrement,
  itemcode string not null,
  shopcode string not null,
  genreid string not null,
  itemurl string not null,
  imgurl string not null,
  date integer not null
);


