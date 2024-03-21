from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, synonym
from queue import Queue

Base = declarative_base()


def create_dynamic_table(table_name, columns):
    """
    Dynamically creates a SQLAlchemy table based on the provided table name and columns.

    Args:
        table_name (str): Name of the table to be created.
        columns (dict): Dictionary where keys are column names and values are SQLAlchemy column types.

    Returns:
        class: Dynamically created table class.
    """

    class DynamicTable(Base):
        __tablename__ = table_name
        id = Column(Integer, primary_key=True, autoincrement=True)
        
        # Create columns dynamically
        for column_name, column_type in columns.items():
            column = Column(column_type)
            setattr(DynamicTable, column_name, column)
            setattr(DynamicTable, f'{column_name}_syn', synonym(column_name))
            
    return DynamicTable


def load_data_to_database(queue_dict, table_name, columns, database_url='sqlite:///:memory:'):
    """
    Loads data from a dictionary of queues into the database table specified by table_name.

    Args:
        queue_dict (dict): Dictionary where keys are column names and values are Queue objects containing data for each column.
        table_name (str): Name of the database table.
        columns (dict): Dictionary where keys are column names and values are SQLAlchemy column types.
        database_url (str, optional): Database connection string. Defaults to 'sqlite:///:memory:' (in-memory SQLite database).
    """
    
    Base = declarative_base()
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)

    DynamicTableClass = create_dynamic_table(table_name, columns)
    Session = sessionmaker(bind=engine)
    session = Session()

    while not all(queue.empty() for queue in queue_dict.values()):
        row = {key: queue.get() for key, queue in queue_dict.items()}
        table_row = DynamicTableClass(**row)
        session.add(table_row)

    session.commit()
    session.close()
