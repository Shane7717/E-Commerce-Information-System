drop table if exists Reviews_Reviewed_Written cascade;
drop table if exists O_Contain_P cascade;
drop table if exists Orders_Placed_Shipped cascade;
drop table if exists P_BelongTo_C cascade;
drop table if exists M_Make_P cascade;
drop table if exists Customers;
drop table if exists Products;
drop table if exists Shipments;
drop table if exists Manufactures;
drop table if exists Categories;

create table Customers(
	cid integer primary key,
	name varchar(128),
	address varchar(256),
	phone_number varchar(128),
	payment_method varchar(128)
);

create table Products(
	pid integer primary key,
	name varchar(128),
	price decimal,
	in_stock integer,
	brand varchar(128),
	description varchar(512)
);

create table Reviews_Reviewed_Written (
	rid integer primary key,
	score integer,
	review_date date,
	review_time time,
	review_text varchar(512),
	pid integer not null,
	cid integer not null,
	foreign key (pid) references Products(pid),
	foreign key (cid) references Customers(cid)
);

create table Shipments(
	sid integer primary key,
	type varchar(128),
	origin_city varchar(128),
	destination_city varchar(128),
	company varchar(128)
);

create table Orders_Placed_Shipped(
	order_id integer primary key,
	order_date date,
	order_time time,
	quantity integer,
	total_amount decimal(8,2),
	description varchar(512),
	cid integer not null,
	sid integer not null unique,
	foreign key (cid) references Customers(cid),
	foreign key (sid) references Shipments(sid)
);

create table Manufactures(
	name varchar(128),
	city varchar(128),
	primary key (name, city)
);

create table M_Make_P(
	pid integer,
	manufacture_name varchar(128),
	manufacture_city varchar(128),
	primary key (pid, manufacture_name, manufacture_city),
	foreign key (pid) references Products(pid),
	foreign key (manufacture_name, manufacture_city) references Manufactures(name, city)
);

create table Categories(
	name varchar(128) primary key
);

create table O_Contain_P(
	order_id integer,
	pid integer,
	product_quantity integer,
	primary key(order_id, pid),
	foreign key (order_id) references Orders_Placed_Shipped(order_id),
	foreign key (pid) references Products(pid)
);

create table P_BelongTo_C(
	pid integer,
	category varchar(128),
	primary key (pid, category),
	foreign key (pid) references Products(pid),
	foreign key (category) references Categories(name)
);
