from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
Model = declarative_base()


class PolicySpiderUrlInfo(Model):
    __tablename__ = 'policy_spider_url_info'

    id_ = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    task_id = Column(Integer)
    type1 = Column(String(64))
    type2 = Column(String(64))
    type3 = Column(String(64))
    type4 = Column(String(64))
    type5 = Column(String(64))
    url = Column(Text)
    insert_time = Column(DateTime)
    from_url = Column(String(255))

    def __init__(self, task_id, type1, type2, type3, type4, type5):
        self.task_id = task_id
        self.type1 = type1
        self.type2 = type2
        self.type3 = type3
        self.type4 = type4
        self.type5 = type5

    def __repr__(self):
        return '<PolicySpiderUrlInfo %r>' % self.task_id


class PolicySpiderTaskInfo(Model):
    __tablename__ = 'policy_spider_task_info'
    id_ = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    task_id = Column(Integer)
    state = Column(Integer)
    type1 = Column(String(64))
    type2 = Column(String(64))
    type3 = Column(String(64))
    type4 = Column(String(64))
    type5 = Column(String(64))

    rules_organization = Column(String(512))
    rules_subject = Column(String(512))
    rules_keywords = Column(String(512))
    rules_file_number = Column(String(512))
    rules_create_date = Column(String(512))
    rules_release_date = Column(String(512))
    rules_enforcement_date = Column(String(512))
    rules_invalid_date = Column(String(512))
    rules_index_number = Column(String(512))
    rules_author = Column(String(512))

    url = Column(Text)
    insert_time = Column(DateTime)

    def __init__(self, task_id, type1, type2, type3, type4, type5):
        self.task_id = task_id
        self.type1 = type1
        self.type2 = type2
        self.type3 = type3
        self.type4 = type4
        self.type5 = type5

    def __repr__(self):
        return '<PolicySpiderTaskInfo %r>' % self.task_id


class PolicySpiderDataInfo(Model):
    __tablename__ = 'policy_spider_data_info'
    id_ = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    task_id = Column(Integer)
    state = Column(Integer)
    type1 = Column(String(64))
    type2 = Column(String(64))
    type3 = Column(String(64))
    type4 = Column(String(64))
    type5 = Column(String(64))

    title = Column(String(1024))
    content = Column(Text)
    author = Column(String(1024))
    organization = Column(String(1024))
    subject = Column(String(1024))
    keywords = Column(String(1024))
    file_number = Column(String(1024))
    create_date = Column(String(1024))
    release_date = Column(String(1024))
    enforcement_date = Column(String(1024))
    invalid_date = Column(String(1024))
    index_number = Column(String(1024))

    image_path = Column(String(1024))
    attachment = Column(String(1024))

    url = Column(Text)
    insert_time = Column(DateTime)

    def __init__(self, task_id, type1, type2, type3, type4, type5):
        self.task_id = task_id
        self.type1 = type1
        self.type2 = type2
        self.type3 = type3
        self.type4 = type4
        self.type5 = type5

    def __repr__(self):
        return '<PolicySpiderTaskInfo %r>' % self.task_id
