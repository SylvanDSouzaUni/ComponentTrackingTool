import sqlite3
from pathlib import Path

# Function to define path to inventory database
database_path = Path(__file__).with_name("WSG_database.db")


# Reusable function to return a connection to the database
def get_connection():
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


# Function to define structure of database
def create_schema():
    with get_connection() as connection:
        connection.executescript("""
        
            create table if not exists users (
                username text primary key,
                display_name text not null,
                password_hash text not null,
                role text not null check (role IN('ADMIN', 'ENGINEER', 'WAREHOUSE'))
            );
            
            create table if not exists components (
                sku integer primary key,
                component_name text not null,
                unit text not null default 'each',
                min_stock integer not null default 0 check(min_stock >= 0),
                stock integer not null default 0 check(stock>=0),
                condition_status text not null check (condition_status IN('DAMAGED', 'EXPIRED', 'OBSOLETE', 'REPAIRING', 'FUNCTIONAL'))
            );
                
            create table if not exists orders (
                order_id integer primary key autoincrement,
                sku integer not null,
                quantity integer not null check (quantity > 0),
                ordered_by text not null,
                ordered_at float not null,
                received_at float,
                received_by text,
                status text not null default 'ORDERED' check (status IN ('ORDERED', 'RECEIVED')),
                foreign key (sku) references components(sku),
                foreign key (ordered_by) references users(username),
                foreign key (received_by) references users(username)
            );
                
            create table if not exists requests (
                request_id integer primary key autoincrement,
                component_name text not null,
                requested_by text not null,
                requested_at float not null,
                sku integer,
                reviewed_by text,
                reviewed_at float,
                request_state text default 'REQUESTED' check (request_state IN ('REQUESTED', 'ACCEPTED', 'REJECTED')),
                foreign key (requested_by) references users(username),
                foreign key (reviewed_by) references users(username)
            );
                
            create table if not exists audit_logs (
                audit_id integer primary key autoincrement,
                timestamp float not null,
                actor text not null,
                actor_role text not null check (actor_role IN ('ADMIN', 'ENGINEER', 'WAREHOUSE')),
                action text not null
            );
        

        """)



