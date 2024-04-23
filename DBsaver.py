from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoSuchTableError, OperationalError
from sqlalchemy.sql import insert

Base = declarative_base()

def create_table(table_name, columns):
    # Check if the table already exists in metadata
    table = None
    if table_name in Base.metadata.tables:
        table = Base.metadata.tables[table_name]

    else:
        # Create table columns dynamically
        attrs = {'__tablename__': table_name, 'id': Column(Integer, primary_key=True)}
        for name, col_type in columns.items():
            attrs[name] = Column(col_type)

        # Create the class dynamically with Base as the parent
        DynamicTable = type('DynamicTable', (Base,), attrs)
        DynamicTable.__tablename__ = table_name  # Set __tablename__ attribute explicitly
        table = DynamicTable

    # Return the dynamically created class
    return table

def save_data(row, table, database_URL="sqlite:///:memory:"):
    full_db_url = 'sqlite:///' + database_URL
    engine = create_engine(full_db_url, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Construct an insert statement
    stmt = insert(table).values(**row)

    # Execute the statement
    session.execute(stmt)
    session.commit()
    session.close()

def load_db(full_db_path, table_name):
    full_db_url = 'sqlite:///' + full_db_path
    try:
        engine = create_engine(full_db_url)
        metadata = MetaData()
        metadata.reflect(bind=engine)
        try:
            load_table = Table(table_name, metadata, autoload=True, autoload_with=engine)
            return load_table
        except NoSuchTableError:
            print(f"Table '{table_name}' does not exist in the database.")
            return None
    except OperationalError:
        print(f"Database '{full_db_path}' does not exist or is not accessible.")
        return None
    
def create_session(table):
    Session = sessionmaker(bind=table.bind)
    session = Session()
    return session