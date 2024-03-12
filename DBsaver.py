from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect


Base = declarative_base()

def create_table(table_name, columns):
    # Create table columns dynamically
    attrs = {'__tablename__': table_name, 'id': Column(Integer, primary_key=True)}
    for name, col_type in columns.items():
        attrs[name] = Column(col_type)

    # Create the class dynamically with Base as the parent
    DynamicTable = type('DynamicTable', (Base,), attrs)
    DynamicTable.__tablename__ = table_name  # Set __tablename__ attribute explicitly
    
    # Return the dynamically created class
    return DynamicTable

def save_data(queue_dict, table, database_URL="sqlite:///:memory:"):
    engine = create_engine(database_URL, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    last_row = None

    while not all(queue.empty() for queue in queue_dict.values()):
        row = {key: queue.get() for key, queue in queue_dict.items()}
        table_row = table(**row)
        session.add(table_row)

        # Update last_table_row with the latest table_row
        last_row = row

    session.commit()
    session.close()

    return last_row