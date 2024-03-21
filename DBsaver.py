from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
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

def save_data(queue_dict, table, database_URL="sqlite:///:memory:"):
    engine = create_engine(database_URL, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    Queue_Max_size = len(queue_dict)
    Queue_size = len(queue_dict)
    first_row = None

    while not all(queue.empty() for queue in queue_dict.values()):
        row = {key: queue.get() for key, queue in queue_dict.items()}

        # Construct an insert statement
        stmt = insert(table).values(**row)
        # Execute the statement
        session.execute(stmt)
        # Update last_table_row with the first_row

        if Queue_size == Queue_Max_size:
            first_row = row

        Queue_size = Queue_size-1

    session.commit()
    session.close()

    return first_row